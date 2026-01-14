"""
Bot Engine
Motor de ejecución de bots de señales de trading
Maneja el ciclo de vida de los bots: iniciar, detener, monitorear
OPTIMIZADO: Usa Market Data Service centralizado para reducir llamadas a Binance
"""

import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

from market_data_service import market_data_service
from strategy_evaluator import StrategyEvaluator
from telegram_sender import TelegramSender
from database import get_db_connection

class TradingBot:
    """Bot individual de trading"""
    
    def __init__(self, config: Dict):
        """
        Inicializar un bot de trading
        
        Args:
            config: Configuración del bot con campos:
                - id: ID único del bot
                - name: Nombre del bot
                - bot_token: Token de Telegram
                - chat_id: ID del chat de Telegram
                - symbol: Par de trading (ej: BTCUSDT)
                - timeframe: Intervalo de tiempo (1m, 5m, 15m, 1h, 4h, 1d)
                - check_interval: Segundos entre cada verificación
                - strategy: Configuración de la estrategia
        """
        self.config = config
        self.bot_id = config['id']
        self.name = config['name']
        self.symbol = config['symbol']
        self.timeframe = config['timeframe']
        self.check_interval = config['check_interval']
        self.strategy = config['strategy']
        self.ignore_position_tracking = config.get('ignore_position_tracking', False)  # Nuevo campo
        
        # Componentes
        # NO crear MarketDataProvider individual - usar servicio centralizado
        self.evaluator = StrategyEvaluator()
        self.telegram = TelegramSender(config['bot_token'], config['chat_id'])
        
        # Suscribirse al Market Data Service
        market_data_service.subscribe(self.bot_id, self.symbol, self.timeframe)
        
        # Estado
        self.running = False
        self.thread = None
        self.last_check = None
        self.signals_sent = 0
        self.start_time = None
        
        # Tracking de posiciones
        self.in_long_position = False
        self.in_short_position = False
        self.last_signal_type = None
    
    def start(self):
        """Iniciar el bot"""
        if self.running:
            print(f"⚠️ Bot {self.name} already running")
            return
        
        self.running = True
        self.start_time = datetime.now()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        
        print(f"✅ Bot {self.name} started for {self.symbol} on {self.timeframe}")
    
    def stop(self):
        """Detener el bot"""
        if not self.running:
            # Desuscribirse del Market Data Service
            market_data_service.unsubscribe(self.bot_id, self.symbol, self.timeframe)
            return

        self.running = False
        if self.thread:
            self.thread.join(timeout=5)

        print(f"⏹️ Bot {self.name} stopped")
    
    def _run_loop(self):
        """Loop principal del bot"""
        print(f"🚀 [THREAD START] Bot '{self.name}' thread initiated")
        print(f"   Bot ID: {self.bot_id}")
        print(f"   Symbol: {self.symbol}")
        print(f"   Timeframe: {self.timeframe}")
        print(f"   Check Interval: {self.check_interval}s")
        print(f"   Running: {self.running}")
        
        # Mensaje de inicio
        start_msg = f"🤖 Bot '{self.name}' iniciado\n📊 Monitoreando {self.symbol} en {self.timeframe}\n⏰ Verificará cada {self.check_interval}s"
        self.telegram.send_message(start_msg, disable_notification=True)
        
        iteration = 0
        while self.running:
            iteration += 1
            try:
                print(f"\n{'='*60}")
                print(f"🔄 [ITERATION #{iteration}] Bot '{self.name}' - {datetime.now().strftime('%H:%M:%S')}")
                print(f"   Running status: {self.running}")
                print(f"{'='*60}")
                
                self._check_signals()
                self.last_check = datetime.now()
                
                # Actualizar estadísticas en la base de datos
                self._update_stats()
                
                print(f"⏳ Sleeping for {self.check_interval}s before next check...")
                print(f"   Next check at: {(datetime.now() + timedelta(seconds=self.check_interval)).strftime('%H:%M:%S')}")
                
                # Esperar antes del próximo chequeo
                time.sleep(self.check_interval)
                
            except Exception as e:
                print(f"❌ Error in bot {self.name} loop: {e}")
                import traceback
                traceback.print_exc()
                print(f"⏳ Sleeping {self.check_interval}s after error...")
                time.sleep(self.check_interval)
        
        print(f"🛑 [THREAD END] Bot '{self.name}' thread terminated (running={self.running})")
    
    def _check_signals(self):
        """Verificar señales del mercado"""
        print(f"🔍 Checking signals for {self.name} ({self.symbol} on {self.timeframe})...")
        
        # Obtener datos del Market Data Service (NO de Binance directamente)
        df = market_data_service.get_data(self.symbol, self.timeframe)
        
        if df is None or df.empty:
            print(f"⚠️ No market data available for {self.symbol}/{self.timeframe}")
            return
        
        current_price = float(df['close'].iloc[-1])
        print(f"💰 Current price: ${current_price}")
        
        try:
            # Evaluar estrategias
            entry_long = self.evaluator.evaluate_strategy(df, self.strategy, 'entry_long')
            exit_long = self.evaluator.evaluate_strategy(df, self.strategy, 'exit_long')
            entry_short = self.evaluator.evaluate_strategy(df, self.strategy, 'entry_short')
            exit_short = self.evaluator.evaluate_strategy(df, self.strategy, 'exit_short')
            
            print(f"📊 Strategy results: LONG_ENTRY={entry_long}, LONG_EXIT={exit_long}, SHORT_ENTRY={entry_short}, SHORT_EXIT={exit_short}")
            print(f"📍 Current positions: in_long={self.in_long_position}, in_short={self.in_short_position}")
            print(f"🎚️ Position tracking: {'DISABLED (Test Mode)' if self.ignore_position_tracking else 'ENABLED (Professional Mode)'}")
            
            # Lógica de señales
            signal_sent = False
            
            # Señal de entrada LONG
            # Modo Prueba: ignora tracking, siempre envía si condición es True
            # Modo Profesional: solo envía si NO está en posición
            if entry_long and (self.ignore_position_tracking or not self.in_long_position):
                message = self.evaluator.generate_signal_message(
                    self.symbol,
                    "ENTRADA LONG",
                    current_price,
                    "🟢 Condiciones de entrada alcista detectadas"
                )
                
                if self.telegram.send_message(message):
                    self.in_long_position = True
                    self.in_short_position = False
                    self.last_signal_type = 'ENTRY_LONG'
                    self.signals_sent += 1
                    signal_sent = True
                    self._save_signal('ENTRY_LONG', message)
                    print(f"🟢 LONG signal sent for {self.symbol} at ${current_price}")
            
            # Señal de salida LONG
            elif exit_long and (self.ignore_position_tracking or self.in_long_position):
                message = self.evaluator.generate_signal_message(
                    self.symbol,
                    "SALIDA LONG",
                    current_price,
                    "⚪ Condiciones de salida alcista detectadas"
                )
                
                if self.telegram.send_message(message):
                    self.in_long_position = False
                    self.last_signal_type = 'EXIT_LONG'
                    self.signals_sent += 1
                    signal_sent = True
                    self._save_signal('EXIT_LONG', message)
                    print(f"⚪ LONG exit signal sent for {self.symbol} at ${current_price}")
            
            # Señal de entrada SHORT
            elif entry_short and (self.ignore_position_tracking or not self.in_short_position):
                message = self.evaluator.generate_signal_message(
                    self.symbol,
                    "ENTRADA SHORT",
                    current_price,
                    "🔴 Condiciones de entrada bajista detectadas"
                )
                
                if self.telegram.send_message(message):
                    self.in_short_position = True
                    self.in_long_position = False
                    self.last_signal_type = 'ENTRY_SHORT'
                    self.signals_sent += 1
                    signal_sent = True
                    self._save_signal('ENTRY_SHORT', message)
                    print(f"🔴 SHORT signal sent for {self.symbol} at ${current_price}")
            
            # Señal de salida SHORT
            elif exit_short and (self.ignore_position_tracking or self.in_short_position):
                message = self.evaluator.generate_signal_message(
                    self.symbol,
                    "SALIDA SHORT",
                    current_price,
                    "⚪ Condiciones de salida bajista detectadas"
                )
                
                if self.telegram.send_message(message):
                    self.in_short_position = False
                    self.last_signal_type = 'EXIT_SHORT'
                    self.signals_sent += 1
                    signal_sent = True
                    self._save_signal('EXIT_SHORT', message)
                    print(f"⚪ SHORT exit signal sent for {self.symbol} at ${current_price}")
            
            if not signal_sent:
                print(f"ℹ️ No signal conditions met for {self.symbol}")
            
        except Exception as e:
            print(f"❌ Error checking signals for {self.name}: {e}")
            import traceback
            traceback.print_exc()
    
    def toggle_position_tracking(self, enabled: bool):
        """
        Cambiar el modo de tracking de posiciones
        
        Args:
            enabled: False = Modo Profesional (tracking ON), True = Modo Prueba (tracking OFF)
        """
        self.ignore_position_tracking = enabled
        mode = "Test Mode (tracking OFF)" if enabled else "Professional Mode (tracking ON)"
        print(f"🎚️ Bot '{self.name}' position tracking changed to: {mode}")
        
        # Actualizar en la base de datos
        try:
            numeric_id = int(self.bot_id.replace('bot_', ''))
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE signal_bots
                SET ignore_position_tracking = ?
                WHERE id = ?
            ''', (1 if enabled else 0, numeric_id))
            
            conn.commit()
            conn.close()
            print(f"✅ Position tracking mode updated in database for bot {self.bot_id}")
        except Exception as e:
            print(f"❌ Error updating position tracking in database: {e}")
    
    def _save_signal(self, signal_type: str, signal_text: str):
        """Guardar señal en la base de datos"""
        try:
            # Extraer ID numérico del bot_id
            numeric_id = int(self.bot_id.replace('bot_', ''))
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO bot_signals (bot_id, signal_type, signal_text, created_at)
                VALUES (?, ?, ?, ?)
            ''', (numeric_id, signal_type, signal_text, datetime.now().isoformat()))
            
            # Actualizar última señal en la tabla de bots
            cursor.execute('''
                UPDATE signal_bots
                SET last_signal = ?, last_signal_text = ?, signals_sent = signals_sent + 1
                WHERE id = ?
            ''', (datetime.now().timestamp() * 1000, signal_text, numeric_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error saving signal: {e}")
    
    def _update_stats(self):
        """Actualizar estadísticas del bot en la base de datos"""
        try:
            if not self.start_time:
                return
            
            uptime = int((datetime.now() - self.start_time).total_seconds())
            numeric_id = int(self.bot_id.replace('bot_', ''))
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE signal_bots
                SET uptime = ?, signals_sent = ?
                WHERE id = ?
            ''', (uptime, self.signals_sent, numeric_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error updating stats: {e}")


class BotEngine:
    """Motor que maneja múltiples bots de trading"""
    
    def __init__(self):
        """Inicializar el motor de bots"""
        self.bots: Dict[str, TradingBot] = {}
        self.lock = threading.Lock()
    
    def start_bot(self, config: Dict) -> bool:
        """
        Iniciar un nuevo bot
        
        Args:
            config: Configuración del bot
        
        Returns:
            True si se inició exitosamente, False en caso contrario
        """
        bot_id = config['id']
        
        with self.lock:
            # Si el bot ya existe, detenerlo primero
            if bot_id in self.bots:
                self.bots[bot_id].stop()
                del self.bots[bot_id]
            
            # Crear y arrancar nuevo bot
            try:
                bot = TradingBot(config)
                bot.start()
                self.bots[bot_id] = bot
                return True
            except Exception as e:
                print(f"❌ Error starting bot {bot_id}: {e}")
                return False
    
    def stop_bot(self, bot_id: str) -> bool:
        """
        Detener un bot
        
        Args:
            bot_id: ID del bot a detener
        
        Returns:
            True si se detuvo exitosamente, False en caso contrario
        """
        with self.lock:
            if bot_id in self.bots:
                try:
                    self.bots[bot_id].stop()
                    del self.bots[bot_id]
                    return True
                except Exception as e:
                    print(f"❌ Error stopping bot {bot_id}: {e}")
                    return False
            return False
    
    def restart_bot(self, bot_id: str) -> bool:
        """
        Reiniciar un bot (útil después de actualizar su configuración)
        
        Args:
            bot_id: ID del bot a reiniciar
        
        Returns:
            True si se reinició exitosamente, False en caso contrario
        """
        # Obtener configuración actual del bot de la base de datos
        try:
            numeric_id = int(bot_id.replace('bot_', ''))
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT name, bot_token, chat_id, symbol, timeframe, check_interval, strategy
                FROM signal_bots
                WHERE id = ?
            ''', (numeric_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return False
            
            config = {
                'id': bot_id,
                'name': row[0],
                'bot_token': row[1],
                'chat_id': row[2],
                'symbol': row[3],
                'timeframe': row[4],
                'check_interval': row[5],
                'strategy': json.loads(row[6]) if row[6] else {}
            }
            
            # Detener y reiniciar
            self.stop_bot(bot_id)
            return self.start_bot(config)
            
        except Exception as e:
            print(f"❌ Error restarting bot {bot_id}: {e}")
            return False
    
    def get_bot_status(self, bot_id: str) -> Optional[Dict]:
        """
        Obtener estado de un bot
        
        Args:
            bot_id: ID del bot
        
        Returns:
            Diccionario con el estado del bot o None si no existe
        """
        with self.lock:
            if bot_id in self.bots:
                bot = self.bots[bot_id]
                return {
                    'id': bot.bot_id,
                    'name': bot.name,
                    'running': bot.running,
                    'signals_sent': bot.signals_sent,
                    'last_check': bot.last_check.isoformat() if bot.last_check else None,
                    'uptime': int((datetime.now() - bot.start_time).total_seconds()) if bot.start_time else 0
                }
            return None
    
    def force_check(self, bot_id: str) -> Optional[Dict]:
        """
        Forzar verificación inmediata del mercado en un bot
        
        Args:
            bot_id: ID del bot
        
        Returns:
            Resultado de la verificación o None si el bot no existe
        """
        with self.lock:
            if bot_id not in self.bots:
                return None
            
            bot = self.bots[bot_id]
        
        # Ejecutar chequeo fuera del lock para no bloquear otros bots
        try:
            print(f"🔍 Forcing market check for bot {bot.name}...")
            print(f"📋 Bot status: in_long={bot.in_long_position}, in_short={bot.in_short_position}")
            
            # IMPORTANTE: Resetear posiciones para forzar evaluación limpia
            # Esto permite que el bot envíe señales incluso si ya había enviado antes
            print(f"🔄 Resetting bot positions for fresh evaluation...")
            bot.in_long_position = False
            bot.in_short_position = False
            
            # Realizar la verificación
            bot._check_signals()
            
            return {
                'success': True,
                'bot_name': bot.name,
                'symbol': bot.symbol,
                'timeframe': bot.timeframe,
                'last_check': datetime.now().isoformat(),
                'message': 'Market checked successfully. If conditions were met, a signal was sent.'
            }
            
        except Exception as e:
            print(f"❌ Error forcing check for bot {bot_id}: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e)
            }
    
    def stop_all_bots(self):
        """Detener todos los bots"""
        with self.lock:
            for bot_id in list(self.bots.keys()):
                try:
                    self.bots[bot_id].stop()
                except Exception as e:
                    print(f"❌ Error stopping bot {bot_id}: {e}")
            
            self.bots.clear()
            print("🛑 All bots stopped")
    
    def load_active_bots(self):
        """
        Cargar y arrancar automáticamente todos los bots con status='active' desde la base de datos
        Esta función debe llamarse al iniciar el servidor
        """
        print("\n" + "="*60)
        print("🚀 CARGANDO BOTS ACTIVOS DESDE LA BASE DE DATOS...")
        print("="*60)
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, bot_token, chat_id, symbol, timeframe, check_interval, strategy, status, ignore_position_tracking
                FROM signal_bots
                WHERE status = 'active'
            ''')
            
            active_bots = cursor.fetchall()
            conn.close()
            
            if not active_bots:
                print("📭 No hay bots activos en la base de datos")
                print("="*60 + "\n")
                return 0
            
            print(f"📊 Se encontraron {len(active_bots)} bot(s) activo(s)")
            print("-"*60)
            
            started_count = 0
            for row in active_bots:
                try:
                    bot_id = f'bot_{row[0]}'
                    config = {
                        'id': bot_id,
                        'name': row[1],
                        'bot_token': row[2],
                        'chat_id': row[3],
                        'symbol': row[4],
                        'timeframe': row[5],
                        'check_interval': row[6],
                        'strategy': json.loads(row[7]) if row[7] else {},
                        'ignore_position_tracking': bool(row[9]) if len(row) > 9 else False
                    }
                    
                    print(f"\n🤖 Bot: {config['name']}")
                    print(f"   ID: {bot_id}")
                    print(f"   Symbol: {config['symbol']}")
                    print(f"   Timeframe: {config['timeframe']}")
                    print(f"   Check Interval: {config['check_interval']}s ({config['check_interval']//60}min)")
                    
                    # Arrancar el bot
                    if self.start_bot(config):
                        started_count += 1
                        print(f"   ✅ Bot arrancado exitosamente")
                    else:
                        print(f"   ❌ Error al arrancar bot")
                        
                except Exception as e:
                    print(f"   ❌ Error procesando bot {row[1]}: {e}")
                    import traceback
                    traceback.print_exc()
            
            print("-"*60)
            print(f"✅ {started_count} de {len(active_bots)} bots arrancados exitosamente")
            print("="*60 + "\n")
            
            return started_count
            
        except Exception as e:
            print(f"❌ Error cargando bots activos: {e}")
            import traceback
            traceback.print_exc()
            print("="*60 + "\n")
            return 0

"""
Market Data Service - Sistema centralizado de datos de mercado
Reduce llamadas a Binance API compartiendo datos entre múltiples bots
"""

import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple
import requests
import pandas as pd


class MarketDataService:
    """
    Servicio centralizado para obtener y cachear datos de mercado.
    
    - Singleton: Una sola instancia para toda la aplicación
    - Thread-safe: Múltiples bots pueden acceder simultáneamente
    - Workers inteligentes: Un worker por cada par (símbolo, timeframe)
    - Auto-gestión: Inicia/detiene workers según demanda
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Implementación Singleton thread-safe"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializar servicio (solo una vez)"""
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self.cache: Dict[Tuple[str, str], Tuple[pd.DataFrame, datetime]] = {}
        self.workers: Dict[Tuple[str, str], threading.Thread] = {}
        self.subscribers: Dict[Tuple[str, str], List[str]] = {}
        self.worker_stop_flags: Dict[Tuple[str, str], threading.Event] = {}
        self.lock = threading.Lock()
        
        print("🚀 Market Data Service inicializado")
    
    def subscribe(self, bot_id: str, symbol: str, timeframe: str):
        """
        Suscribir un bot a datos de mercado.
        Si es el primer suscriptor, inicia un worker.
        
        Args:
            bot_id: ID único del bot
            symbol: Par de trading (ej: BTCUSDT)
            timeframe: Marco temporal (ej: 15m, 1h)
        """
        key = (symbol, timeframe)
        
        with self.lock:
            # Agregar a lista de suscriptores
            if key not in self.subscribers:
                self.subscribers[key] = []
            
            if bot_id not in self.subscribers[key]:
                self.subscribers[key].append(bot_id)
                print(f"📊 Bot {bot_id} suscrito a {symbol}/{timeframe}")
            
            # Iniciar worker si no existe
            if key not in self.workers or not self.workers[key].is_alive():
                self._start_worker(symbol, timeframe)
    
    def unsubscribe(self, bot_id: str, symbol: str, timeframe: str):
        """
        Desuscribir un bot de datos de mercado.
        Si no quedan suscriptores, detiene el worker.
        
        Args:
            bot_id: ID único del bot
            symbol: Par de trading
            timeframe: Marco temporal
        """
        key = (symbol, timeframe)
        
        with self.lock:
            if key in self.subscribers and bot_id in self.subscribers[key]:
                self.subscribers[key].remove(bot_id)
                print(f"📉 Bot {bot_id} desuscrito de {symbol}/{timeframe}")
            
            # Detener worker si no hay suscriptores
            if key in self.subscribers and len(self.subscribers[key]) == 0:
                self._stop_worker(symbol, timeframe)
    
    def get_data(self, symbol: str, timeframe: str) -> Optional[pd.DataFrame]:
        """
        Obtener datos del cache (thread-safe).
        
        Args:
            symbol: Par de trading
            timeframe: Marco temporal
            
        Returns:
            DataFrame con datos OHLCV o None si no hay datos
        """
        key = (symbol, timeframe)
        
        with self.lock:
            if key in self.cache:
                data, timestamp = self.cache[key]
                age = (datetime.now() - timestamp).total_seconds()
                
                # Verificar que los datos no sean muy viejos
                max_age = self._get_max_cache_age(timeframe)
                if age <= max_age:
                    return data.copy()  # Retornar copia para evitar modificaciones
                else:
                    print(f"⚠️ Datos de {symbol}/{timeframe} obsoletos ({age:.0f}s)")
        
        return None
    
    def get_stats(self) -> Dict:
        """Obtener estadísticas del servicio"""
        with self.lock:
            active_workers = sum(1 for t in self.workers.values() if t.is_alive())
            total_subscribers = sum(len(subs) for subs in self.subscribers.values())
            
            stats = {
                'active_pairs': len(self.subscribers),
                'active_workers': active_workers,
                'total_subscribers': total_subscribers,
                'cached_datasets': len(self.cache),
                'pairs': {}
            }
            
            for key, subs in self.subscribers.items():
                symbol, timeframe = key
                stats['pairs'][f"{symbol}/{timeframe}"] = {
                    'subscribers': len(subs),
                    'cached': key in self.cache
                }
            
            return stats
    
    def _start_worker(self, symbol: str, timeframe: str):
        """
        Iniciar worker para actualizar datos periódicamente.
        
        Args:
            symbol: Par de trading
            timeframe: Marco temporal
        """
        key = (symbol, timeframe)
        
        # Crear flag de parada
        stop_flag = threading.Event()
        self.worker_stop_flags[key] = stop_flag
        
        def worker_loop():
            """Loop del worker que actualiza datos"""
            print(f"🟢 Worker iniciado para {symbol}/{timeframe}")
            
            # Hacer primera descarga inmediatamente
            try:
                data = self._fetch_from_binance(symbol, timeframe)
                with self.lock:
                    self.cache[key] = (data, datetime.now())
                print(f"✅ Datos iniciales cargados: {symbol}/{timeframe}")
            except Exception as e:
                print(f"❌ Error en carga inicial {symbol}/{timeframe}: {e}")
            
            # Loop de actualización
            update_interval = self._get_update_interval(timeframe)
            
            while not stop_flag.is_set():
                try:
                    # Verificar si aún hay suscriptores
                    with self.lock:
                        if key not in self.subscribers or len(self.subscribers[key]) == 0:
                            break
                        subscriber_count = len(self.subscribers[key])
                    
                    # Descargar datos de Binance
                    data = self._fetch_from_binance(symbol, timeframe)
                    
                    # Guardar en cache
                    with self.lock:
                        self.cache[key] = (data, datetime.now())
                    
                    current_price = data['close'].iloc[-1]
                    print(f"🔄 {symbol}/{timeframe} actualizado → ${current_price:,.2f} ({subscriber_count} bots)")
                    
                except Exception as e:
                    print(f"❌ Error en worker {symbol}/{timeframe}: {e}")
                
                # Esperar antes de la próxima actualización
                stop_flag.wait(timeout=update_interval)
            
            print(f"🔴 Worker detenido para {symbol}/{timeframe}")
        
        # Iniciar thread
        thread = threading.Thread(target=worker_loop, daemon=True, name=f"Worker-{symbol}-{timeframe}")
        thread.start()
        self.workers[key] = thread
    
    def _stop_worker(self, symbol: str, timeframe: str):
        """
        Detener worker para un par específico.
        
        Args:
            symbol: Par de trading
            timeframe: Marco temporal
        """
        key = (symbol, timeframe)
        
        if key in self.worker_stop_flags:
            self.worker_stop_flags[key].set()
            del self.worker_stop_flags[key]
        
        if key in self.workers:
            del self.workers[key]
        
        if key in self.cache:
            del self.cache[key]
        
        print(f"🛑 Worker detenido: {symbol}/{timeframe}")
    
    def _fetch_from_binance(self, symbol: str, timeframe: str, limit: int = 500) -> pd.DataFrame:
        """
        Descargar datos de Binance API.
        
        Args:
            symbol: Par de trading
            timeframe: Marco temporal
            limit: Número de velas a descargar
            
        Returns:
            DataFrame con datos OHLCV
        """
        url = "https://api.binance.com/api/v3/klines"
        params = {
            'symbol': symbol,
            'interval': timeframe,
            'limit': limit
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Convertir a DataFrame
        df = pd.DataFrame(data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])
        
        # Seleccionar y convertir columnas
        df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['open'] = pd.to_numeric(df['open'], errors='coerce')
        df['high'] = pd.to_numeric(df['high'], errors='coerce')
        df['low'] = pd.to_numeric(df['low'], errors='coerce')
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
        
        return df
    
    def _get_update_interval(self, timeframe: str) -> int:
        """
        Determinar cada cuánto actualizar según el timeframe.
        Timeframes cortos = actualización más frecuente
        
        Args:
            timeframe: Marco temporal
            
        Returns:
            Intervalo de actualización en segundos
        """
        intervals = {
            '1m': 30,    # Actualizar cada 30 segundos
            '3m': 45,    # Actualizar cada 45 segundos
            '5m': 60,    # Actualizar cada 60 segundos
            '15m': 120,  # Actualizar cada 2 minutos
            '30m': 180,  # Actualizar cada 3 minutos
            '1h': 300,   # Actualizar cada 5 minutos
            '2h': 480,   # Actualizar cada 8 minutos
            '4h': 600,   # Actualizar cada 10 minutos
            '6h': 900,   # Actualizar cada 15 minutos
            '8h': 1200,  # Actualizar cada 20 minutos
            '12h': 1800, # Actualizar cada 30 minutos
            '1d': 3600,  # Actualizar cada 1 hora
        }
        return intervals.get(timeframe, 120)
    
    def _get_max_cache_age(self, timeframe: str) -> int:
        """
        Determinar edad máxima del cache según timeframe.
        
        Args:
            timeframe: Marco temporal
            
        Returns:
            Edad máxima en segundos
        """
        # El cache debe ser válido por al menos 2x el intervalo de actualización
        return self._get_update_interval(timeframe) * 2
    
    def shutdown(self):
        """Detener todos los workers y limpiar recursos"""
        print("🛑 Deteniendo Market Data Service...")
        
        with self.lock:
            # Detener todos los workers
            for key in list(self.worker_stop_flags.keys()):
                symbol, timeframe = key
                self._stop_worker(symbol, timeframe)
            
            # Limpiar todo
            self.cache.clear()
            self.subscribers.clear()
            self.workers.clear()
            self.worker_stop_flags.clear()
        
        print("✅ Market Data Service detenido")


# Instancia global singleton
market_data_service = MarketDataService()


if __name__ == "__main__":
    """Test del servicio"""
    print("=== TEST MARKET DATA SERVICE ===\n")
    
    # Simular 3 bots suscritos a BTC/15m
    service = market_data_service
    
    service.subscribe("bot_1", "BTCUSDT", "15m")
    service.subscribe("bot_2", "BTCUSDT", "15m")
    service.subscribe("bot_3", "ETHUSDT", "1h")
    
    # Esperar a que se carguen datos
    time.sleep(5)
    
    # Obtener datos
    btc_data = service.get_data("BTCUSDT", "15m")
    if btc_data is not None:
        print(f"\n✅ BTC Data: {len(btc_data)} velas, último precio: ${btc_data['close'].iloc[-1]:,.2f}")
    
    # Ver estadísticas
    stats = service.get_stats()
    print(f"\n📊 Estadísticas:")
    print(f"   Pares activos: {stats['active_pairs']}")
    print(f"   Workers activos: {stats['active_workers']}")
    print(f"   Total suscriptores: {stats['total_subscribers']}")
    
    # Esperar un poco más
    time.sleep(10)
    
    # Desuscribir bots
    service.unsubscribe("bot_1", "BTCUSDT", "15m")
    service.unsubscribe("bot_2", "BTCUSDT", "15m")
    
    # Esperar a que se detenga el worker
    time.sleep(3)
    
    # Shutdown
    service.shutdown()

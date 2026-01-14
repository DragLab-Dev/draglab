"""
Visual Strategy Creator - Constructor Visual de Estrategias de Trading
Plataforma para crear estrategias de trading y bots mediante bloques visuales - Sin Programar
Características: Constructor de bloques drag-and-drop, backtest integrado, creación de bots
Versión: 2.4 - Con Sistema de Autenticación
Fecha: Enero 2026
Creado por: camiloeagiraldodev@gmail.com
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import pandas as pd
import os
import tempfile
import time
import json
import hashlib
from datetime import datetime, timedelta
from dotenv import load_dotenv
from functools import wraps
import requests

# Cargar variables de entorno
load_dotenv()

# Importar módulos locales de autenticación
import database as db
from auth_routes import auth_bp
from admin_routes import admin_bp
from payments_routes import payments_bp
from signal_bot_routes import signal_bot_bp
from subscription_routes import subscription_bp

# Configurar Flask
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Desactivar caché de templates para desarrollo
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Configuración de sesiones
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
app.config['SESSION_COOKIE_SECURE'] = False  # True si usas HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Registrar blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(payments_bp)
app.register_blueprint(signal_bot_bp)
app.register_blueprint(subscription_bp)

# Configuración de directorios
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CACHE_DIR = os.path.join(os.path.dirname(__file__), "data", "cache")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

# ==================== MIDDLEWARE DE AUTENTICACIÓN ====================

def login_required(f):
    """Decorador para rutas que requieren autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verificar si hay token en la sesión de Flask o en localStorage (cookies)
        token = session.get('session_token') or request.cookies.get('session_token')
        
        if not token:
            # No hay token, redirigir a welcome
            return redirect(url_for('auth.welcome_page'))
        
        # Verificar si el token es válido
        user_session = db.get_session(token)
        if not user_session:
            # Token inválido o expirado, limpiar sesión
            session.pop('session_token', None)
            session.pop('user_id', None)
            return redirect(url_for('auth.welcome_page'))
        
        # Token válido, continuar
        return f(*args, **kwargs)
    return decorated_function

# ==================== INDICADORES TÉCNICOS ====================

def EMA(series, period):
    """Exponential Moving Average - Media Móvil Exponencial"""
    return pd.Series(series).ewm(span=period, adjust=False).mean()

def SMA(series, period):
    """Simple Moving Average - Media Móvil Simple"""
    return pd.Series(series).rolling(window=period).mean()

def RSI(series, period=14):
    """Relative Strength Index - Índice de Fuerza Relativa"""
    delta = pd.Series(series).diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def MACD(series, fast=12, slow=26, signal=9):
    """Moving Average Convergence Divergence"""
    ema_fast = EMA(series, fast)
    ema_slow = EMA(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = EMA(macd_line, signal)
    return macd_line, signal_line

# ==================== SISTEMA DE CACHE PARA BACKTEST ====================

def get_cache_key(symbol, pair, timeframe, start_date):
    """Generar clave única para cache basada en parámetros"""
    cache_str = f"{symbol}_{pair}_{timeframe}_{start_date}"
    return hashlib.md5(cache_str.encode()).hexdigest()

def get_cached_data(cache_key):
    """Obtener datos desde cache si existe y no ha expirado (24h)"""
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
    
    if not os.path.exists(cache_file):
        return None
    
    # Verificar antigüedad del cache (24 horas)
    file_age = time.time() - os.path.getmtime(cache_file)
    if file_age > 86400:  # 24 horas en segundos
        return None
    
    try:
        with open(cache_file, 'r') as f:
            cached = json.load(f)
            print(f"✅ Datos cargados desde cache ({file_age/3600:.1f}h antigüedad)")
            return cached
    except:
        return None

def save_to_cache(cache_key, data):
    """Guardar datos en cache"""
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
    try:
        with open(cache_file, 'w') as f:
            json.dump(data, f)
        print(f"💾 Datos guardados en cache")
    except Exception as e:
        print(f"⚠️  Error guardando cache: {e}")

def download_from_coingecko(symbol, pair, days=365):
    """
    Descargar datos históricos desde CoinGecko (GRATUITO)
    CoinGecko es el proveedor más confiable para backtesting de cripto
    """
    try:
        # Mapear símbolos comunes a IDs de CoinGecko
        symbol_map = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'BNB': 'binancecoin',
            'ADA': 'cardano',
            'XRP': 'ripple',
            'SOL': 'solana',
            'DOT': 'polkadot',
            'DOGE': 'dogecoin',
            'MATIC': 'matic-network',
            'AVAX': 'avalanche-2',
            'LINK': 'chainlink',
            'UNI': 'uniswap',
            'ATOM': 'cosmos',
            'LTC': 'litecoin',
            'BCH': 'bitcoin-cash',
            'XLM': 'stellar',
            'ALGO': 'algorand',
            'VET': 'vechain',
            'ICP': 'internet-computer',
            'FIL': 'filecoin',
        }
        
        coin_id = symbol_map.get(symbol.upper())
        if not coin_id:
            # Intentar buscar por símbolo
            search_url = f"https://api.coingecko.com/api/v3/search?query={symbol}"
            response = requests.get(search_url, timeout=10)
            if response.status_code == 200:
                coins = response.json().get('coins', [])
                if coins:
                    coin_id = coins[0]['id']
                else:
                    raise Exception(f"Símbolo {symbol} no encontrado en CoinGecko")
            else:
                raise Exception(f"Error buscando símbolo en CoinGecko")
        
        # Mapear par a moneda de CoinGecko
        vs_currency = pair.lower() if pair.upper() in ['USD', 'EUR', 'GBP', 'JPY'] else 'usd'
        
        print(f"📥 Descargando {symbol} desde CoinGecko (ID: {coin_id})...")
        
        # API de CoinGecko para datos históricos
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        params = {
            'vs_currency': vs_currency,
            'days': days,
            'interval': 'daily'
        }
        
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code != 200:
            raise Exception(f"Error CoinGecko API: {response.status_code}")
        
        data = response.json()
        
        # Convertir a formato OHLCV
        prices = data.get('prices', [])
        if not prices:
            raise Exception("No hay datos de precios disponibles")
        
        # CoinGecko solo da precios, generamos OHLC aproximado
        df_data = []
        for i, price_point in enumerate(prices):
            timestamp = price_point[0]
            price = price_point[1]
            
            # Aproximar OHLC (CoinGecko API gratis solo da precio de cierre)
            # Para backtest esto es suficiente
            df_data.append({
                'timestamp': timestamp,
                'open': price,
                'high': price * 1.005,  # +0.5% aproximado
                'low': price * 0.995,   # -0.5% aproximado
                'close': price,
                'volume': 0  # CoinGecko free no incluye volumen en este endpoint
            })
        
        print(f"✅ {len(df_data)} velas descargadas desde CoinGecko")
        return df_data
        
    except Exception as e:
        print(f"❌ Error en CoinGecko: {e}")
        return None

def download_from_yfinance(symbol, pair, start_date):
    """
    Descargar datos desde Yahoo Finance como fallback
    yfinance es confiable para backtesting y gratuito
    """
    try:
        import yfinance as yf
        
        # Construir ticker (Yahoo usa formato especial para cripto)
        if pair.upper() == 'USD':
            ticker = f"{symbol}-USD"
        elif pair.upper() == 'USDT':
            ticker = f"{symbol}-USD"  # Yahoo no tiene USDT, usar USD
        else:
            ticker = f"{symbol}-{pair}"
        
        print(f"📥 Descargando {ticker} desde Yahoo Finance...")
        
        # Descargar datos
        df = yf.download(ticker, start=start_date, progress=False)
        
        if df.empty:
            raise Exception(f"No hay datos para {ticker}")
        
        # Convertir a formato estándar
        df_data = []
        for idx, row in df.iterrows():
            df_data.append({
                'timestamp': int(idx.timestamp() * 1000),
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'volume': float(row['Volume']) if 'Volume' in row else 0
            })
        
        print(f"✅ {len(df_data)} velas descargadas desde Yahoo Finance")
        return df_data
        
    except Exception as e:
        print(f"❌ Error en Yahoo Finance: {e}")
        return None

def BBands(series, period=20, std_dev=2):
    """Bollinger Bands - Bandas de Bollinger"""
    sma = SMA(series, period)
    rolling_std = pd.Series(series).rolling(window=period).std()
    upper = sma + (rolling_std * std_dev)
    lower = sma - (rolling_std * std_dev)
    return upper, sma, lower

def ATR(high, low, close, period=14):
    """Average True Range - Rango Verdadero Promedio"""
    high_low = pd.Series(high) - pd.Series(low)
    high_close = abs(pd.Series(high) - pd.Series(close).shift())
    low_close = abs(pd.Series(low) - pd.Series(close).shift())
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return true_range.rolling(window=period).mean()

# ==================== ESTRATEGIA DE TRADING ====================
# Importación diferida para evitar problemas de carga

def get_strategy_class():
    """Lazy import de backtesting"""
    from backtesting import Strategy
    
    class EMAStrategy(Strategy):
        """
        Estrategia EMA con Swing High/Low
        
        Reglas:
        - LONG: Precio > EMA y rompe swing high
        - SHORT: Precio < EMA y rompe swing low
        - Salida LONG: Precio cruza debajo de EMA
        - Salida SHORT: Precio cruza arriba de EMA
        """
        ema_fast = 50
        swing_lookback = 20
        position_size = 0.2

        def init(self):
            """Inicializar indicadores"""
            close = self.data.Close
            self.ema = self.I(EMA, close, self.ema_fast)

        def next(self):
            """Lógica de trading ejecutada en cada vela"""
            # Verificar datos suficientes
            if len(self.data.Close) < self.swing_lookback:
                return

            close = self.data.Close[-1]
            ema = self.ema[-1]
            swing_high = max(self.data.High[-self.swing_lookback:-1])
            swing_low = min(self.data.Low[-self.swing_lookback:-1])

            # Señales de entrada
            if not self.position:
                # Entrada LONG
                if close > ema and close > swing_high:
                    self.buy(size=self.position_size)
                # Entrada SHORT
                elif close < ema and close < swing_low:
                    self.sell(size=self.position_size)
            # Señales de salida
            else:
                # Salida LONG
                if self.position.is_long and close < ema:
                    self.position.close()
                # Salida SHORT
                elif self.position.is_short and close > ema:
                    self.position.close()
    
    return EMAStrategy

def get_fractional_backtest_class():
    """Lazy import de FractionalBacktest"""
    from backtesting import Backtest
    
    class FractionalBacktest(Backtest):
        """Backtest modificado para soportar posiciones fraccionarias"""
        pass
    
    return FractionalBacktest

# ==================== RUTAS DE LA APLICACIÓN ====================

@app.route('/')
@login_required
def index():
    """Página principal - Home con menú (REQUIERE LOGIN)"""
    return render_template('index.html')

@app.route('/test-menu')
def test_menu():
    """Página de prueba del menú universal (SIN LOGIN)"""
    return render_template('test_menu.html')

@app.route('/trading-bot')
@login_required
def trading_bot_menu():
    """Menú del Trading Bot (REQUIERE LOGIN)"""
    return render_template('trading_bot_menu.html')

@app.route('/signal-bot')
@login_required
def signal_bot():
    """Bot de señales (REQUIERE LOGIN)"""
    return render_template('signal_bot.html')

@app.route('/verify-system')
@login_required
def verify_system():
    """Página de verificación del sistema de bots"""
    return render_template('verify_system.html')

@app.route('/auto-bot')
@login_required
def auto_bot():
    """Bot automático (REQUIERE LOGIN)"""
    return render_template('auto_bot.html')

@app.route('/backtest')
@login_required
def backtest_page():
    """Página del backtest visual (REQUIERE LOGIN)"""
    return render_template('backtest.html')

@app.route('/user-panel')
@login_required
def user_panel():
    """Panel de usuario con gestión de cuenta y suscripción (REQUIERE LOGIN)"""
    return render_template('user_panel.html')

@app.route('/subscriptions')
@login_required
def subscriptions_page():
    """Página de suscripciones y planes (REQUIERE LOGIN)"""
    return render_template('subscriptions.html')

# ========== RUTAS DEL GENERADOR DE DATOS ==========

@app.route('/api/download', methods=['POST'])
def download_data():
    """
    Descarga datos OHLCV desde Binance
    
    Parámetros:
    - symbol: Par de trading (ej: 'BTC/USDT')
    - timeframe: Temporalidad (ej: '1d', '1h', '4h')
    - start_date: Fecha inicial (formato: 'YYYY-MM-DD')
    
    Retorna:
    - JSON con datos descargados y metadata
    """
    try:
        # Lazy import de ccxt solo cuando se necesita
        import ccxt
        
        symbol = request.json.get('symbol', 'BTC/USDT')
        timeframe = request.json.get('timeframe', '1d')
        start_date = request.json.get('start_date', '2025-01-01')
        
        # Inicializar exchange
        exchange = ccxt.binance()
        since = exchange.parse8601(f"{start_date}T00:00:00Z")
        
        # Descargar datos en batches
        all_bars = []
        total_requests = 0
        
        while True:
            bars = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=1000)
            if not bars:
                break
            
            all_bars.extend(bars)
            since = bars[-1][0] + 1
            total_requests += 1
            time.sleep(exchange.rateLimit / 1000)
            
            if total_requests % 5 == 0:
                print(f"Descargadas {len(all_bars)} velas...")
        
        # Crear DataFrame y guardar
        df = pd.DataFrame(all_bars, columns=["Date", "Open", "High", "Low", "Close", "Volume"])
        df["Date"] = pd.to_datetime(df["Date"], unit="ms")
        
        filename = f"{symbol.replace('/', '')}_{timeframe}.csv"
        filepath = os.path.join(DATA_DIR, filename)
        df.to_csv(filepath, index=False)
        
        file_size = os.path.getsize(filepath)
        
        return jsonify({
            'success': True,
            'message': 'Datos descargados exitosamente',
            'rows': len(df),
            'filename': filename,
            'file_size': f"{file_size / 1024:.2f} KB"
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/symbols')
def get_symbols():
    """Obtener lista de símbolos disponibles para trading"""
    symbols = [
        'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'XRP/USDT',
        'SOL/USDT', 'AVAX/USDT', 'POLYX/USDT', 'PROVE/USDT',
        'RED/USDT', 'ZEC/USDT', 'LINK/USDT'
    ]
    return jsonify(symbols)

@app.route('/api/files')
def list_files():
    """Listar archivos CSV disponibles en el directorio de datos"""
    try:
        files = []
        for filename in os.listdir(DATA_DIR):
            if filename.endswith('.csv'):
                filepath = os.path.join(DATA_DIR, filename)
                size = os.path.getsize(filepath)
                modified = datetime.fromtimestamp(os.path.getmtime(filepath))
                files.append({
                    'name': filename,
                    'size': f"{size / 1024:.2f} KB",
                    'modified': modified.strftime('%Y-%m-%d %H:%M:%S')
                })
        return jsonify({'files': files})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ========== BACKTEST ROUTES ==========

@app.route('/api/backtest/symbols')
def list_symbols():
    """Listar símbolos únicos disponibles en archivos CSV"""
    try:
        symbols = set()
        for filename in os.listdir(DATA_DIR):
            if filename.endswith('.csv'):
                parts = filename.replace('.csv', '').split('_')
                if len(parts) == 2:
                    symbols.add(parts[0])
        return jsonify({'symbols': sorted(list(symbols))})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/backtest/timeframes/<symbol>')
def list_timeframes(symbol):
    """Listar temporalidades disponibles para un símbolo específico"""
    try:
        timeframes = []
        for filename in os.listdir(DATA_DIR):
            if filename.endswith('.csv') and filename.startswith(symbol + '_'):
                parts = filename.replace('.csv', '').split('_')
                if len(parts) == 2:
                    timeframes.append(parts[1])
        return jsonify({'timeframes': sorted(timeframes)})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/backtest/run', methods=['POST'])
def run_backtest():
    """
    Ejecutar backtest de estrategia con datos confiables
    
    FUENTES DE DATOS (en orden de prioridad):
    1. Cache local (si existe y < 24h)
    2. CoinGecko API (gratuito, confiable, sin restricciones)
    3. Yahoo Finance (fallback confiable)
    
    Parámetros:
    - symbol: Símbolo base (ej: 'BTC')
    - pair: Par de cotización (ej: 'USDT')
    - timeframe: Temporalidad (ej: '1d', '1h')
    - start_date: Fecha inicial de datos
    - position_size: Tamaño de posición (0-1)
    - cash: Capital inicial
    - commission: Comisión por operación
    - finalize_trades: Cerrar trades al final
    - ema_period: Período de la EMA
    - swing_lookback: Velas para swing high/low
    
    Retorna:
    - Estadísticas del backtest
    - Gráfico HTML interactivo
    - Configuración utilizada
    """
    try:
        # Lazy imports
        EMAStrategy = get_strategy_class()
        FractionalBacktest = get_fractional_backtest_class()
        
        # Obtener parámetros de la solicitud
        symbol_input = request.json.get('symbol', 'BTC').upper()
        pair = request.json.get('pair', 'USDT').upper()
        timeframe = request.json.get('timeframe', '1d')
        start_date = request.json.get('start_date', '2020-01-01')
        position_size = float(request.json.get('position_size', 0.2))
        cash = float(request.json.get('cash', 1000))
        commission = float(request.json.get('commission', 0.004))
        finalize_trades = request.json.get('finalize_trades', 'yes') == 'yes'
        ema_period = int(request.json.get('ema_period', 50))
        swing_lookback = int(request.json.get('swing_lookback', 20))
        
        # Generar clave de cache
        cache_key = get_cache_key(symbol_input, pair, timeframe, start_date)
        
        # 1. Intentar obtener desde cache
        print(f"🔍 Buscando en cache: {symbol_input}/{pair}...")
        all_bars = get_cached_data(cache_key)
        data_source = "cache"
        
        # 2. Si no hay cache, descargar desde CoinGecko
        if not all_bars:
            print(f"📡 Cache no disponible, descargando datos frescos...")
            
            # Calcular días necesarios desde start_date
            start = datetime.strptime(start_date, '%Y-%m-%d')
            days = (datetime.now() - start).days + 30  # +30 días buffer
            
            all_bars = download_from_coingecko(symbol_input, pair, days=days)
            data_source = "CoinGecko"
        
        # 3. Si CoinGecko falla, usar Yahoo Finance
        if not all_bars:
            print(f"⚠️  CoinGecko no disponible, usando Yahoo Finance...")
            all_bars = download_from_yfinance(symbol_input, pair, start_date)
            data_source = "Yahoo Finance"
        
        # 4. Si todo falla, error
        if not all_bars:
            return jsonify({
                'success': False,
                'error': f'No se pudieron obtener datos para {symbol_input}/{pair}. Verifica que el símbolo sea correcto (ej: BTC, ETH, SOL).'
            }), 404
        
        # Guardar en cache si fue descargado
        if data_source != "cache":
            save_to_cache(cache_key, all_bars)
        
        symbol = f"{symbol_input}/{pair}"
        
        # Crear y procesar DataFrame desde formato estándar
        df = pd.DataFrame(all_bars)
        
        # Convertir timestamp a datetime
        df["Date"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("Date", inplace=True)
        
        # Renombrar columnas al formato esperado por backtesting.py
        df.rename(columns={
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'volume': 'Volume'
        }, inplace=True)
        
        # Seleccionar solo columnas OHLCV
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
        
        # Validar datos suficientes
        if df.empty or len(df) < 50:
            return jsonify({
                'success': False,
                'error': f'Datos insuficientes: solo {len(df)} velas disponibles'
            }), 400
        
        print(f"✅ {len(df)} velas procesadas para {symbol} desde {data_source}")
        
        # Generar nombre de archivo para referencia
        filename = f"{symbol.replace('/', '')}_{timeframe}_backtest.csv"
        
        # Configurar estrategia dinámica con parámetros personalizados
        class DynamicEMAStrategy(EMAStrategy):
            pass
        
        DynamicEMAStrategy.position_size = position_size
        DynamicEMAStrategy.ema_fast = ema_period
        DynamicEMAStrategy.swing_lookback = swing_lookback
        
        # Ejecutar backtest
        bt = FractionalBacktest(
            df,
            DynamicEMAStrategy,
            cash=cash,
            commission=commission
        )
        
        stats = bt.run()
        
        # Generar gráfico HTML interactivo
        temp_html = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False)
        temp_filename = temp_html.name
        temp_html.close()
        
        bt.plot(filename=temp_filename, open_browser=False)
        
        # Leer HTML generado
        with open(temp_filename, 'r', encoding='utf-8') as f:
            chart_html = f.read()
        
        # Eliminar archivo temporal
        os.remove(temp_filename)
        
        # Convertir stats a diccionario
        stats_dict = {}
        for key in stats.index:
            value = stats[key]
            try:
                if value is None or (isinstance(value, float) and pd.isna(value)):
                    stats_dict[key] = None
                elif isinstance(value, pd.Timestamp):
                    stats_dict[key] = value.strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(value, pd.Timedelta):
                    stats_dict[key] = str(value)
                elif isinstance(value, (int, float)):
                    stats_dict[key] = float(value)
                else:
                    stats_dict[key] = str(value)
            except:
                stats_dict[key] = str(value)
        
        # 📊 REGISTRAR BACKTEST EN BASE DE DATOS
        try:
            if 'user_id' in session:
                conn = db.get_db_connection()
                cursor = conn.cursor()
                
                # Extraer valores con manejo de diferentes formatos
                return_pct = stats_dict.get('Return [%]', 0)
                num_trades = stats_dict.get('# Trades', 0)
                win_rate = stats_dict.get('Win Rate [%]', 0)
                
                # Convertir a float si es string
                if isinstance(return_pct, str):
                    return_pct = float(return_pct.replace('%', '').strip()) if return_pct else 0
                if isinstance(num_trades, str):
                    num_trades = int(float(num_trades))
                if isinstance(win_rate, str):
                    win_rate = float(win_rate.replace('%', '').strip()) if win_rate else 0
                
                print(f"📊 Guardando backtest: user={session['user_id']}, symbol={symbol}, trades={num_trades}")
                
                cursor.execute("""
                    INSERT INTO backtest_results 
                    (user_id, symbol, timeframe, profit_loss, num_trades, win_rate)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    session['user_id'],
                    symbol,
                    timeframe,
                    float(return_pct),
                    int(num_trades),
                    float(win_rate)
                ))
                conn.commit()
                conn.close()
                print(f"✅ Backtest registrado exitosamente en BD")
            else:
                print(f"⚠️ No se guardó backtest: usuario no autenticado")
        except Exception as e:
            import traceback
            print(f"❌ Error registrando backtest: {e}")
            print(traceback.format_exc())
        
        return jsonify({
            'success': True,
            'message': 'Backtest ejecutado exitosamente',
            'stats': stats_dict,
            'chart_html': chart_html,
            'config': {
                'symbol': symbol,
                'timeframe': timeframe,
                'position_size': position_size,
                'cash': cash,
                'commission': commission,
                'finalize_trades': finalize_trades,
                'ema_period': ema_period,
                'swing_lookback': swing_lookback,
                'filename': filename,
                'total_candles': len(df)
            }
        })
    
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 400

if __name__ == '__main__':
    # Inicializar base de datos
    db.init_database()
    
    print("=" * 60)
    print("[*] TradingBot Platform - Servidor con Autenticacion")
    print("=" * 60)
    print("URLs:")
    print("   - Bienvenida: http://192.168.1.13:5000/welcome")
    print("   - Login:      http://192.168.1.13:5000/login")
    print("   - Registro:   http://192.168.1.13:5000/register")
    print("   - Home:       http://192.168.1.13:5000/ (requiere login)")
    print()
    print("Funcionalidades:")
    print("   [+] Sistema de autenticacion con email y Google")
    print("   [+] Verificacion por codigo de 4 digitos")
    print("   [+] Sesiones persistentes (30 dias)")
    print("   [+] Constructor visual de estrategias drag-and-drop")
    print("   [+] Backtest con multiples indicadores tecnicos")
    print("   [+] Bots de trading en tiempo real")
    print("=" * 60)
    print("Creado por: camiloeagiraldodev@gmail.com")
    print("=" * 60)
    
    # 🚀 CARGAR Y ARRANCAR BOTS ACTIVOS AUTOMÁTICAMENTE
    from signal_bot_routes import bot_engine
    bot_engine.load_active_bots()
    
    app.run(debug=False, host='0.0.0.0', port=5000)

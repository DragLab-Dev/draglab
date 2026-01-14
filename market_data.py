"""
Market Data Provider
Obtiene datos del mercado de Binance y calcula indicadores técnicos
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class MarketDataProvider:
    """Proveedor de datos de mercado desde Binance"""
    
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3"
        self.cache = {}  # Cache simple para evitar llamadas excesivas
        self.cache_duration = 60  # segundos
    
    def get_klines(self, symbol: str, interval: str, limit: int = 500) -> pd.DataFrame:
        """
        Obtener velas (candlesticks) de Binance
        
        Args:
            symbol: Par de trading (ej: BTCUSDT)
            interval: Intervalo de tiempo (1m, 5m, 15m, 1h, 4h, 1d)
            limit: Número de velas a obtener
        
        Returns:
            DataFrame con columnas: open, high, low, close, volume
        """
        cache_key = f"{symbol}_{interval}"
        now = datetime.now()
        
        # Verificar cache
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if (now - cached_time).total_seconds() < self.cache_duration:
                return cached_data.copy()
        
        try:
            url = f"{self.base_url}/klines"
            params = {
                'symbol': symbol,
                'interval': interval,
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
            
            # Seleccionar y convertir columnas relevantes
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['open'] = pd.to_numeric(df['open'], errors='coerce')
            df['high'] = pd.to_numeric(df['high'], errors='coerce')
            df['low'] = pd.to_numeric(df['low'], errors='coerce')
            df['close'] = pd.to_numeric(df['close'], errors='coerce')
            df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
            
            # Guardar en cache
            self.cache[cache_key] = (df, now)
            
            return df
            
        except Exception as e:
            print(f"Error fetching market data: {e}")
            # Retornar cache antiguo si existe
            if cache_key in self.cache:
                return self.cache[cache_key][0].copy()
            raise
    
    def calculate_ema(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Calcular EMA (Exponential Moving Average)"""
        return df['close'].ewm(span=period, adjust=False).mean()
    
    def calculate_sma(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Calcular SMA (Simple Moving Average)"""
        return df['close'].rolling(window=period).mean()
    
    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calcular RSI (Relative Strength Index)"""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """Calcular MACD (Moving Average Convergence Divergence)"""
        ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    def calculate_bollinger_bands(self, df: pd.DataFrame, period: int = 20, std_dev: float = 2) -> Dict[str, pd.Series]:
        """Calcular Bollinger Bands"""
        sma = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()
        
        return {
            'upper': sma + (std * std_dev),
            'middle': sma,
            'lower': sma - (std * std_dev)
        }
    
    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calcular ATR (Average True Range)"""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        
        atr = pd.Series(true_range).rolling(window=period).mean()
        return atr
    
    def find_swing_high(self, df: pd.DataFrame, lookback: int = 5) -> pd.Series:
        """Encontrar máximos locales (Swing Highs)"""
        swing_highs = pd.Series(index=df.index, dtype=float)
        
        for i in range(lookback, len(df) - lookback):
            is_swing_high = True
            for j in range(1, lookback + 1):
                if df['high'].iloc[i] <= df['high'].iloc[i - j] or df['high'].iloc[i] <= df['high'].iloc[i + j]:
                    is_swing_high = False
                    break
            
            if is_swing_high:
                swing_highs.iloc[i] = df['high'].iloc[i]
        
        return swing_highs
    
    def find_swing_low(self, df: pd.DataFrame, lookback: int = 5) -> pd.Series:
        """Encontrar mínimos locales (Swing Lows)"""
        swing_lows = pd.Series(index=df.index, dtype=float)
        
        for i in range(lookback, len(df) - lookback):
            is_swing_low = True
            for j in range(1, lookback + 1):
                if df['low'].iloc[i] >= df['low'].iloc[i - j] or df['low'].iloc[i] >= df['low'].iloc[i + j]:
                    is_swing_low = False
                    break
            
            if is_swing_low:
                swing_lows.iloc[i] = df['low'].iloc[i]
        
        return swing_lows
    
    def get_current_price(self, symbol: str) -> float:
        """Obtener precio actual de un símbolo"""
        try:
            url = f"{self.base_url}/ticker/price"
            params = {'symbol': symbol}
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            return float(data['price'])
            
        except Exception as e:
            print(f"Error getting current price: {e}")
            return 0.0

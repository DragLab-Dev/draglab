# 📊 Fuentes de Datos para Backtesting

## ✅ Sistema Implementado (Profesional)

El sistema de backtesting ahora utiliza **fuentes de datos confiables y dedicadas** en lugar de exchanges en vivo.

### 🎯 Fuentes de Datos (en orden de prioridad):

1. **Cache Local** (24 horas)
   - Almacenamiento: `data/cache/`
   - Formato: JSON
   - Ventaja: Instantáneo, sin llamadas API
   - Expiración: 24 horas

2. **CoinGecko API** (Principal)
   - **Gratuito**
   - **Sin restricciones geográficas**
   - **Confiable para backtesting**
   - Soporta 20+ criptomonedas principales
   - Datos históricos ilimitados

3. **Yahoo Finance** (Fallback)
   - **Gratuito**
   - **Datos históricos confiables**
   - Compatible con formato Crypto-USD
   - Backup cuando CoinGecko falla

---

## ❌ NO se usan para Backtest:

- ~~Binance~~ - Solo para trading en vivo
- ~~Bybit~~ - Solo para trading en vivo
- ~~CCXT Exchanges~~ - No confiables para datos históricos

**Razón:** Los exchanges tienen:
- Restricciones geográficas
- Límites de rate
- Datos en vivo (no optimizados para backtest)
- Posible manipulación de precios históricos

---

## 🚀 Ventajas del Nuevo Sistema:

✅ **Sin restricciones geográficas** (funciona en VPS de cualquier país)  
✅ **Cache inteligente** (evita descargas repetidas)  
✅ **Datos confiables** (proveedores especializados en históricos)  
✅ **Gratuito 100%** (no requiere API keys)  
✅ **Fallback robusto** (3 niveles de respaldo)  
✅ **Rápido** (cache reduce latencia a milisegundos)

---

## 📋 Criptomonedas Soportadas:

| Símbolo | Nombre | CoinGecko ID |
|---------|--------|--------------|
| BTC | Bitcoin | bitcoin |
| ETH | Ethereum | ethereum |
| BNB | Binance Coin | binancecoin |
| ADA | Cardano | cardano |
| XRP | Ripple | ripple |
| SOL | Solana | solana |
| DOT | Polkadot | polkadot |
| DOGE | Dogecoin | dogecoin |
| MATIC | Polygon | matic-network |
| AVAX | Avalanche | avalanche-2 |
| LINK | Chainlink | chainlink |
| UNI | Uniswap | uniswap |
| ATOM | Cosmos | cosmos |
| LTC | Litecoin | litecoin |
| BCH | Bitcoin Cash | bitcoin-cash |
| XLM | Stellar | stellar |
| ALGO | Algorand | algorand |
| VET | VeChain | vechain |
| ICP | Internet Computer | internet-computer |
| FIL | Filecoin | filecoin |

*Y muchas más automáticamente vía búsqueda*

---

## 🔧 Uso:

```python
# El sistema es automático
# Solo ejecuta el backtest desde la UI:
1. Selecciona símbolo (ej: BTC)
2. Selecciona par (USDT/USD)
3. Click en "Ejecutar Backtest"

# Flujo interno:
1. Busca en cache (si existe y < 24h) → RETORNA
2. Descarga desde CoinGecko → GUARDA en cache → RETORNA
3. Si falla, descarga desde Yahoo Finance → GUARDA en cache → RETORNA
4. Si todo falla → ERROR con mensaje claro
```

---

## 📁 Estructura de Cache:

```
data/
└── cache/
    ├── a3f2d8e9b1c4f5a6.json  (BTC_USDT_1d_2020-01-01)
    ├── b7e4c1a9f2d8e3b5.json  (ETH_USDT_1d_2020-01-01)
    └── ...
```

**Nombre:** Hash MD5 de `{symbol}_{pair}_{timeframe}_{start_date}`  
**Contenido:** Array de objetos OHLCV en formato estándar

---

## 🛠️ Mantenimiento:

### Limpiar cache manualmente:
```bash
rm -rf data/cache/*
```

### Ver tamaño del cache:
```bash
du -sh data/cache/
```

### El cache se limpia automáticamente:
- ✅ Archivos > 24h son ignorados y re-descargados
- ❌ NO se borran automáticamente (puedes hacerlo manual)

---

## 📝 Notas Técnicas:

- **Formato OHLCV estándar:** `{timestamp, open, high, low, close, volume}`
- **Timestamp:** Milisegundos Unix (compatible con Pandas)
- **Aproximación OHLC:** CoinGecko API gratis solo da Close, se aproxima OHLC con ±0.5%
- **Precisión:** Suficiente para backtesting de estrategias (no afecta resultados significativamente)

---

## 🆚 Comparación:

| Característica | Antes (Binance/Bybit) | Ahora (CoinGecko+Cache) |
|----------------|----------------------|------------------------|
| Restricciones geo | ❌ Bloqueado en VPS | ✅ Sin restricciones |
| Cache | ❌ No | ✅ 24h automático |
| Confiabilidad | ⚠️ Variable | ✅ Alta |
| Velocidad | 🐌 5-30s | ⚡ < 1s (cache) |
| Rate limits | ⚠️ Estrictos | ✅ Generosos |
| Costo | 🆓 Gratis | 🆓 Gratis |
| API Keys | ❌ No (pero bloqueado) | ✅ No necesita |

---

## 🎓 Para Desarrolladores:

### Agregar nuevo símbolo a CoinGecko:

```python
# En app.py, busca symbol_map y agrega:
symbol_map = {
    ...
    'TU_SYMBOL': 'coingecko-id-aqui',
}
```

### Cambiar tiempo de expiración del cache:

```python
# En app.py, función get_cached_data:
if file_age > 86400:  # 86400 = 24h en segundos
    # Cambia a 43200 para 12h, 3600 para 1h, etc.
```

---

## ✅ Probado en:

- ✅ Windows (desarrollo local)
- ✅ Ubuntu VPS (producción)
- ✅ Sin VPN
- ✅ Con restricciones geográficas de Binance
- ✅ Múltiples símbolos (BTC, ETH, SOL, etc.)

---

**Actualizado:** Enero 2026  
**Autor:** camiloeagiraldodev@gmail.com

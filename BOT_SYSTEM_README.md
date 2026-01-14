# 🤖 Sistema de Bots de Señales de Trading

## 📋 Descripción

Sistema completo de bots automatizados que:
- ✅ Lee datos del mercado en tiempo real desde Binance
- ✅ Evalúa estrategias creadas con bloques visuales
- ✅ Envía señales automáticas a Telegram cuando se cumplen las condiciones
- ✅ Monitorea múltiples pares y timeframes simultáneamente

---

## 🚀 Instalación y Configuración

### 1. **Instalar Dependencias**

```bash
pip install -r requirements.txt
```

### 2. **Crear las Tablas de Base de Datos**

```bash
python update_database_bots.py
```

Esto creará:
- **`signal_bots`**: Tabla con la configuración de cada bot
- **`bot_signals`**: Historial de todas las señales enviadas

### 3. **Configurar Bot de Telegram**

#### 📱 Crear un Bot de Telegram:

1. Abre Telegram y busca [@BotFather](https://t.me/BotFather)
2. Envía `/newbot`
3. Sigue las instrucciones para obtener tu **Bot Token**
4. Guarda el token (formato: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

#### 💬 Obtener el Chat ID:

**Opción 1 (Automática desde la UI):**
- En la interfaz web, haz clic en "Obtener Chat ID"
- El sistema lo detectará automáticamente

**Opción 2 (Manual):**
1. Envía un mensaje a tu bot
2. Visita: `https://api.telegram.org/bot<TU_BOT_TOKEN>/getUpdates`
3. Busca el campo `"chat":{"id":...}`

---

## 🎯 Uso del Sistema

### 1. **Crear una Estrategia**

1. Ve a la **Sección 2: Constructor Visual de Estrategias**
2. Arrastra bloques desde la paleta:
   - **Indicadores**: EMA, SMA, RSI, MACD, Bollinger Bands, ATR, Swing
   - **Valores**: Precio, Número, Porcentaje
   - **Comparadores**: Mayor, Menor, Igual, Cruza
   - **Lógicos**: AND, OR, NOT, XOR, NAND, NOR

**Ejemplo de Estrategia Simple:**
```
ENTRADA LONG:
- Precio > EMA(50)
- RSI(14) > 50

SALIDA LONG:
- Precio < EMA(50)
```

### 2. **Crear un Bot**

1. Haz clic en "➕ Crear Nuevo Bot"
2. Completa el formulario:
   - **Nombre**: Ej. "Bot BTC EMA"
   - **Bot Token**: Tu token de @BotFather
   - **Chat ID**: ID del chat/canal
   - **Par**: BTCUSDT, ETHUSDT, etc.
   - **Timeframe**: 1m, 5m, 15m, 1h, 4h, 1d
   - **Intervalo**: Segundos entre chequeos (mín. 10)
3. La estrategia actual se guardará automáticamente

### 3. **Activar el Bot**

1. Haz clic en **"▶️ Activar"**
2. El bot comenzará a:
   - ✅ Monitorear el mercado cada X segundos
   - ✅ Evaluar tu estrategia en tiempo real
   - ✅ Enviar señales a Telegram cuando se cumplan las condiciones

---

## 📊 Estructura del Sistema

### **Archivos Principales:**

```
├── signal_bot_routes.py      # API endpoints (CRUD de bots)
├── bot_engine.py              # Motor de ejecución de bots
├── market_data.py             # Obtención de datos de Binance
├── strategy_evaluator.py     # Evaluación de estrategias
├── telegram_sender.py         # Envío de mensajes a Telegram
└── update_database_bots.py    # Script de migración de BD
```

### **Flujo de Ejecución:**

```
1. Usuario crea bot → Guardado en BD
2. Usuario activa bot → bot_engine.start_bot()
3. Bot inicia thread → Loop cada X segundos
4. market_data.get_klines() → Obtener datos de Binance
5. strategy_evaluator.evaluate() → Evaluar condiciones
6. Si condición = True → telegram_sender.send_message()
7. Guardar señal en BD → Actualizar estadísticas
```

---

## 🔧 Características Técnicas

### **Motor de Bots (bot_engine.py)**
- **Threading**: Cada bot corre en su propio thread
- **Gestión de estado**: Tracking de posiciones (LONG/SHORT)
- **Estadísticas**: Señales enviadas, uptime, última señal
- **Seguridad**: Locks para operaciones concurrentes

### **Evaluador de Estrategias (strategy_evaluator.py)**
- **Sistema de Stack**: Evaluación secuencial de bloques
- **Indicadores Técnicos**: Cálculo dinámico con Pandas
- **Cache**: Evita recalcular indicadores
- **Soporte completo**: Todos los bloques de la UI

### **Datos de Mercado (market_data.py)**
- **API Binance**: Endpoint público `/api/v3/klines`
- **Cache**: Reduce llamadas a la API (60s)
- **Indicadores**: EMA, SMA, RSI, MACD, BB, ATR, Swing Highs/Lows
- **Fallback**: Retorna cache antiguo si hay error

### **Telegram (telegram_sender.py)**
- **Formato HTML**: Mensajes con negrita, emojis
- **Test de conexión**: Verifica token y acceso al chat
- **Manejo de errores**: Reintentos automáticos
- **Sin notificaciones**: Opción para señales silenciosas

---

## 📝 Ejemplos de Estrategias

### **Estrategia 1: Cruce de EMAs**

**ENTRADA LONG:**
```
EMA(20) > EMA(50)
```

**SALIDA LONG:**
```
EMA(20) < EMA(50)
```

### **Estrategia 2: RSI Sobrecompra/Sobreventa**

**ENTRADA LONG:**
```
RSI(14) < 30
```

**ENTRADA SHORT:**
```
RSI(14) > 70
```

### **Estrategia 3: Bollinger Bands**

**ENTRADA LONG:**
```
Precio < BBands(20, 2).lower
```

**ENTRADA SHORT:**
```
Precio > BBands(20, 2).upper
```

### **Estrategia 4: Multi-indicador (Avanzada)**

**ENTRADA LONG:**
```
(Precio > EMA(50)) AND (RSI(14) > 50) AND (MACD > 0)
```

**SALIDA LONG:**
```
(RSI(14) > 70) OR (Precio < EMA(50))
```

---

## ⚠️ Consideraciones Importantes

### **Limitaciones de la API de Binance**

- **Rate Limits**: Máximo 1200 requests/minuto
- **Weight**: Cada llamada consume "weight"
- **IP Bans**: Respetar límites o serás bloqueado temporalmente

**Recomendaciones:**
- ✅ Intervalo mínimo: **10 segundos**
- ✅ Máximo bots simultáneos: **10-15**
- ✅ Usar cache cuando sea posible

### **Trading Real**

⚠️ **ADVERTENCIA**: Este sistema envía **señales automáticas**. NO ejecuta órdenes reales.

Para trading real:
1. Lee las señales de Telegram
2. Valida con tu propio análisis
3. Ejecuta manualmente en tu exchange

### **Seguridad**

- 🔒 Nunca compartas tu Bot Token
- 🔒 Usa variables de entorno en producción
- 🔒 Limita acceso al servidor
- 🔒 Revisa logs regularmente

---

## 🐛 Troubleshooting

### **El bot no envía señales**

1. **Verifica la conexión con Telegram:**
   ```python
   from telegram_sender import TelegramSender
   sender = TelegramSender('tu_token', 'tu_chat_id')
   print(sender.test_connection())
   ```

2. **Revisa los logs del servidor:**
   ```bash
   python app.py
   # Verás mensajes como:
   # ✅ Bot started for BTCUSDT on 15m
   # 🟢 LONG signal sent for BTCUSDT at $45000
   ```

3. **Valida que la estrategia se evalúe:**
   - Agrega `print()` en `strategy_evaluator.py`
   - Verifica que los datos de Binance se obtengan correctamente

### **Error 404 en endpoints**

- Verifica que `signal_bot_routes.py` esté registrado en `app.py`
- Reinicia el servidor Flask

### **Bot no se detiene**

- Usa `bot_engine.stop_all_bots()` al cerrar la app
- Verifica que los threads se unan correctamente

---

## 📈 Monitoreo y Estadísticas

Cada bot registra:
- **Señales enviadas**: Contador total
- **Uptime**: Tiempo activo en segundos
- **Última señal**: Timestamp y texto completo
- **Historial completo**: Tabla `bot_signals`

### **Ver logs en la UI:**

1. Haz clic en "📊 Historial"
2. Verás las últimas 100 señales
3. Exporta para análisis externo

---

## 🚀 Mejoras Futuras

Ideas para expandir el sistema:
- [ ] **Stop Loss / Take Profit** automáticos
- [ ] **Backtesting de bots** antes de activarlos
- [ ] **Alertas por email** además de Telegram
- [ ] **Panel de analytics** con gráficos
- [ ] **Integración con exchanges** para trading real
- [ ] **Machine Learning** para optimizar estrategias
- [ ] **Notificaciones multi-canal** (Discord, Slack, WhatsApp)

---

## 💡 Soporte

**Desarrollador**: camiloeagiraldodev@gmail.com

**Documentación adicional**:
- [API Binance](https://binance-docs.github.io/apidocs/spot/en/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Pandas TA](https://github.com/twopirllc/pandas-ta)

---

## 📄 Licencia

Este software es de uso personal y educativo. No redistribuir sin autorización.

**⚠️ Disclaimer**: El trading de criptomonedas conlleva riesgos. Este software no garantiza ganancias. Úsalo bajo tu propia responsabilidad.

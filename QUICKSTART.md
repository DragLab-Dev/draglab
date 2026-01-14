# 🚀 Guía de Inicio Rápido - Sistema de Bots

## ⚡ Configuración en 5 Pasos

### **Paso 1: Crear las Tablas de Base de Datos**

```bash
python update_database_bots.py
```

**Resultado esperado:**
```
✅ Database tables created successfully!
   - signal_bots: Tabla de bots de trading
   - bot_signals: Tabla de señales enviadas
```

---

### **Paso 2: Probar el Sistema**

```bash
python test_bot_system.py
```

**Esto verificará:**
- ✅ Conexión con Binance API
- ✅ Cálculo de indicadores técnicos
- ✅ Evaluación de estrategias
- ✅ Tablas de base de datos
- ⚠️ Conexión con Telegram (opcional)

---

### **Paso 3: Crear un Bot de Telegram**

1. **Abrir Telegram** y buscar [@BotFather](https://t.me/BotFather)

2. **Enviar:** `/newbot`

3. **Seguir instrucciones:**
   - Nombre del bot: `Mi Bot de Señales`
   - Username: `mi_bot_senales_bot` (debe terminar en "bot")

4. **Guardar el token:**
   ```
   123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

5. **Obtener Chat ID:**
   - Envía un mensaje a tu bot
   - Visita: `https://api.telegram.org/bot<TU_TOKEN>/getUpdates`
   - Copia el número del campo `"chat":{"id":...}`

---

### **Paso 4: Iniciar el Servidor**

```bash
python app.py
```

**Abre en tu navegador:**
```
http://localhost:5000
```

---

### **Paso 5: Crear tu Primer Bot**

#### **5.1 Diseñar Estrategia (Sección 2)**

**Ejemplo simple - Cruce de EMA:**

**Zona de Entrada LONG:**
1. Arrastra **"Precio"** → **"Mayor que (>)"** → **"EMA"** (período: 50)

**Zona de Salida LONG:**
1. Arrastra **"Precio"** → **"Menor que (<)"** → **"EMA"** (período: 50)

#### **5.2 Crear Bot (Sección 3)**

1. Clic en **"➕ Crear Nuevo Bot"**

2. **Completar formulario:**
   ```
   Nombre: Bot BTC EMA
   Bot Token: [tu token de @BotFather]
   Chat ID: [tu chat ID]
   Par: BTCUSDT
   Timeframe: 15m
   Intervalo: 60 (segundos)
   ```

3. Clic en **"💾 Guardar Bot"**

#### **5.3 Activar Bot**

1. Clic en **"▶️ Activar"** en la tarjeta del bot
2. ¡Listo! El bot comenzará a monitorear el mercado

---

## 📱 Mensaje de Ejemplo en Telegram

Cuando se detecte una señal, recibirás:

```
🟢 SEÑAL DE TRADING 🟢

━━━━━━━━━━━━━━━━━
📊 Par: BTCUSDT
📈 Tipo: ENTRADA LONG
💰 Precio: $45,320.50
🕐 Hora: 2026-01-07 15:30:00 UTC
━━━━━━━━━━━━━━━━━

🟢 Condiciones de entrada alcista detectadas

💡 Señal generada automáticamente
⚠️ Haz tu propio análisis antes de operar
```

---

## 🎯 Ejemplos de Estrategias Populares

### **Estrategia 1: RSI Sobreventa**

**Entrada LONG:**
- `RSI(14)` < `Número(30)`

**Salida LONG:**
- `RSI(14)` > `Número(70)`

---

### **Estrategia 2: Doble EMA**

**Entrada LONG:**
- `EMA(20)` > `EMA(50)` **AND** `Precio` > `EMA(20)`

**Salida LONG:**
- `EMA(20)` < `EMA(50)`

---

### **Estrategia 3: Bollinger Bands Bounce**

**Entrada LONG:**
- `Precio` < `Bollinger Lower Band`

**Salida LONG:**
- `Precio` > `Bollinger Middle Band`

---

## ⚙️ Configuración Recomendada

| Timeframe | Intervalo de Chequeo | Pares Recomendados |
|-----------|---------------------|-------------------|
| 1m        | 10-30 segundos      | Scalping (riesgo alto) |
| 5m        | 30-60 segundos      | Day trading |
| 15m       | 60-120 segundos     | **Recomendado** |
| 1h        | 5-10 minutos        | Swing trading |
| 4h        | 15-30 minutos       | Position trading |
| 1d        | 1-2 horas           | Inversión largo plazo |

---

## 🐛 Solución de Problemas

### **Error: "Cannot access 'userBots' before initialization"**

✅ **Solución:** Recarga la página con **Ctrl + Shift + R**

---

### **El bot no envía señales**

1. **Verifica en los logs del servidor:**
   ```
   ✅ Bot started for BTCUSDT on 15m
   ```

2. **Revisa que tu estrategia tenga bloques:**
   - Debe haber al menos 1 bloque en alguna zona

3. **Verifica el token de Telegram:**
   - Usa el botón "🧪 Enviar Mensaje de Prueba"

---

### **Error 401 o 404 en la API**

✅ **Solución:** Inicia sesión en la plataforma primero

---

### **El bot se detiene solo**

- **Causa:** El servidor Flask se cerró
- **Solución:** Mantén `python app.py` corriendo en el terminal

---

## 📊 Monitorear tus Bots

### **Ver estadísticas en tiempo real:**

Cada bot muestra:
- 🟢/⏸️ Estado (Activo/Pausado)
- 📈 Señales enviadas
- ⏱️ Tiempo activo
- 📡 Última señal

### **Ver historial completo:**

1. Clic en **"📊 Historial"**
2. Verás las últimas 100 señales con:
   - Tipo de señal
   - Texto completo
   - Timestamp

---

## 🔒 Seguridad y Buenas Prácticas

### ✅ **SÍ hacer:**

- Prueba estrategias en **modo backtest** primero
- Usa **stop loss** mentales al operar
- Monitorea tus bots regularmente
- Comienza con **timeframes largos** (15m+)
- Limita a **5-10 bots** simultáneos

### ❌ **NO hacer:**

- No compartas tu **Bot Token**
- No uses intervalos menores a **10 segundos**
- No confíes ciegamente en las señales
- No operes sin analizar primero
- No ejecutes 50+ bots a la vez (ban de Binance)

---

## 🚀 Próximos Pasos

Una vez que domines lo básico:

1. **Crea estrategias más complejas** usando operadores lógicos
2. **Combina múltiples indicadores** (EMA + RSI + MACD)
3. **Experimenta con diferentes pares** (BTC, ETH, BNB)
4. **Ajusta timeframes** según tu estilo de trading
5. **Lee el README completo** para funciones avanzadas

---

## 💡 Recursos Adicionales

- **📖 README Completo**: `BOT_SYSTEM_README.md`
- **🧪 Tests**: `python test_bot_system.py`
- **📊 Binance API**: https://binance-docs.github.io/apidocs/
- **🤖 Telegram Bot API**: https://core.telegram.org/bots/api

---

## ✉️ Soporte

**Desarrollador**: camiloeagiraldodev@gmail.com

**Reportar bugs**: Incluye los logs del servidor y descripción del problema

---

¡Disfruta creando estrategias automatizadas! 🚀📈

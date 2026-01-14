# 🚀 Signal Bot - Quick Start Guide

## ✅ El sistema está completamente implementado y listo para usar

### 📋 Paso 1: Verificar el Sistema

```bash
python test_signal_bot.py
```

Deberías ver: **"6/6 tests pasados (100%)"**

### 🚀 Paso 2: Iniciar el Servidor

**Opción A - Inicio Rápido (Recomendado):**
```bash
python start_signal_bot.py
```

**Opción B - Inicio Manual:**
```bash
python app.py
```

El servidor estará disponible en: **http://localhost:5000**

### 🔧 Paso 3: Configurar tu Bot de Telegram

1. **Crear Bot en Telegram:**
   - Abre Telegram y busca [@BotFather](https://t.me/BotFather)
   - Envía el comando: `/newbot`
   - Sigue las instrucciones para nombrar tu bot
   - **Guarda el Bot Token** que te proporciona (ej: `123456:ABC-DEF...`)

2. **Obtener Chat ID:**
   - Envía cualquier mensaje a tu bot (ej: `/start`)
   - En la aplicación web, usa el botón "🔍 Obtener Chat ID"
   - El sistema obtendrá automáticamente tu Chat ID

### 🎯 Paso 4: Crear tu Primera Estrategia

1. **Accede a Signal Bot** desde el menú principal
2. **Arrastra bloques** desde la paleta a las zonas de estrategia:

**Ejemplo - Estrategia Simple de Cruce de EMA:**

```
📊 ENTRADA LONG (Señal de Compra):
   1. Arrastra "Precio" a la zona
   2. Arrastra ">" (Mayor que)
   3. Arrastra "EMA" y configura período 20

💰 SALIDA LONG (Señal de Venta):
   1. Arrastra "Precio" a la zona
   2. Arrastra "<" (Menor que)
   3. Arrastra "EMA" y configura período 20
```

Esto creará señales cuando:
- **COMPRA**: El precio cruza por encima de la EMA(20)
- **VENTA**: El precio cruza por debajo de la EMA(20)

### 🤖 Paso 5: Crear y Activar el Bot

1. **Haz clic en "Crear Nuevo Bot"**
2. **Completa el formulario:**
   ```
   Nombre: Mi Bot BTC
   Bot Token: [Tu token de BotFather]
   Chat ID: [Tu Chat ID]
   Symbol: BTCUSDT
   Timeframe: 15m
   Intervalo de Verificación: 60 (segundos)
   ```

3. **Prueba la conexión:**
   - Click en "📤 Enviar Prueba"
   - Deberías recibir un mensaje en Telegram

4. **Guarda el bot** y luego **actívalo (▶️)**

### 📱 Paso 6: Recibir Señales

Una vez activado, el bot:
- ✅ Monitoreará el mercado cada 60 segundos
- ✅ Evaluará tu estrategia
- ✅ Enviará señales a Telegram cuando se cumplan condiciones

**Ejemplo de señal que recibirás:**
```
🟢 ENTRADA LONG

📊 BTCUSDT
💰 Precio: $42,150.00
🕐 15m | 2026-01-08 14:30:00

📝 Condiciones de entrada alcista detectadas

---
🤖 Signal Bot | DragLab
```

## 📊 Bloques Disponibles

### 📈 Indicadores Técnicos
- **EMA** - Media Móvil Exponencial (configura período)
- **SMA** - Media Móvil Simple (configura período)
- **RSI** - Índice de Fuerza Relativa (típico: 14)
- **MACD** - Convergencia/Divergencia
- **Bollinger** - Bandas de Bollinger
- **ATR** - Average True Range
- **Swing** - Máximos/Mínimos locales

### 💰 Valores
- **Precio** - Precio actual del mercado
- **Número** - Valor numérico fijo
- **Porcentaje** - Valor en porcentaje

### ⚙️ Operadores de Comparación
- **>** Mayor que
- **<** Menor que
- **>=** Mayor o igual
- **<=** Menor o igual
- **==** Igual
- **!=** Diferente
- **✖** Cruza (detecta cruces de líneas)

### 🔗 Operadores Lógicos
- **AND** - Ambas condiciones deben ser verdaderas
- **OR** - Al menos una condición verdadera
- **NOT** - Negación de condición
- **XOR** - Solo una condición verdadera
- **NAND/NOR** - Operadores avanzados

## 🎯 Ejemplos de Estrategias

### 1. Estrategia de Cruce de Medias Móviles
```
ENTRADA LONG:
  EMA(20) > EMA(50)

SALIDA LONG:
  EMA(20) < EMA(50)
```

### 2. Estrategia con RSI
```
ENTRADA LONG:
  RSI(14) < 30  (Sobreventa)
  AND
  Precio > EMA(50)

SALIDA LONG:
  RSI(14) > 70  (Sobrecompra)
```

### 3. Estrategia de Bandas de Bollinger
```
ENTRADA LONG:
  Precio < Bollinger Lower
  AND
  RSI(14) < 40

SALIDA LONG:
  Precio > Bollinger Upper
  OR
  RSI(14) > 60
```

## 🔧 Gestión de Bots

### Ver Estadísticas
Cada bot muestra en tiempo real:
- **Estado**: Activo ✅ / Pausado ⏸️
- **Señales Enviadas**: Contador total
- **Tiempo Activo**: Uptime del bot
- **Última Señal**: Timestamp y tipo

### Modificar Bot
- **✏️ Editar**: Cambiar configuración o estrategia
- **⏸️ Pausar**: Detener temporalmente (sin eliminar)
- **▶️ Activar**: Reanudar el monitoreo
- **📊 Historial**: Ver últimas 100 señales
- **🗑️ Eliminar**: Borrar permanentemente

## 💡 Tips y Mejores Prácticas

### ⚡ Rendimiento
- **Intervalo mínimo**: 60 segundos (evita rate limiting)
- **Timeframes recomendados**: 15m, 1h, 4h para señales confiables
- **Máximo de bots**: Sin límite, pero considera recursos del servidor

### 🎯 Estrategias Efectivas
- ✅ Combina múltiples indicadores para confirmar señales
- ✅ Usa RSI para evitar sobrecompra/sobreventa
- ✅ Añade filtro de tendencia con EMA de período largo
- ❌ Evita estrategias con una sola condición (muchas señales falsas)

### 🔒 Seguridad
- ✅ Nunca compartas tu Bot Token
- ✅ Usa bots separados para pruebas y producción
- ✅ Verifica señales antes de operar
- ✅ Establece stop-loss y take-profit manualmente

## 🐛 Solución de Problemas

### ❌ "No se pueden obtener datos de mercado"
- Verifica tu conexión a internet
- Binance API podría estar temporalmente inactivo
- Espera unos minutos y reactiva el bot

### ❌ "Error al enviar mensaje a Telegram"
- Verifica el Bot Token
- Confirma el Chat ID
- Asegúrate de que el bot no esté bloqueado
- Envía `/start` a tu bot en Telegram

### ❌ "Bot no envía señales"
- Verifica que esté en estado "Activo" (verde)
- Confirma que la estrategia tenga bloques configurados
- Las condiciones de mercado pueden no cumplirse aún
- Revisa el historial para ver si hubo señales anteriores

## 📚 Comandos Útiles

```bash
# Verificar que todo funciona
python test_signal_bot.py

# Crear/actualizar tablas de BD
python update_signal_bots_db.py

# Iniciar servidor con verificación automática
python start_signal_bot.py

# Iniciar servidor directamente
python app.py
```

## 🌐 Endpoints de la API

Si quieres integrar el sistema:

```javascript
// Crear bot
POST /api/signal-bots/create
Body: { name, bot_token, chat_id, symbol, timeframe, check_interval, strategy }

// Listar bots
GET /api/signal-bots/list

// Activar bot
POST /api/signal-bots/activate/<bot_id>

// Obtener Chat ID de Telegram
POST /api/telegram/get-chat-id
Body: { bot_token }

// Enviar mensaje de prueba
POST /api/telegram/send-test
Body: { bot_token, chat_id }
```

## ⚠️ Disclaimer Legal

Este software es **únicamente con fines educativos y de prueba**.

- ❌ NO es asesoramiento financiero
- ❌ NO garantiza ganancias
- ✅ Trading conlleva riesgo de pérdida
- ✅ Usa bajo tu propia responsabilidad

---

## 🎉 ¡Listo!

Tu Signal Bot está completamente configurado y funcionando. 

**¿Necesitas ayuda?** Revisa el archivo `SIGNAL_BOT_README.md` para documentación detallada.

**Creado por:** camiloeagiraldodev@gmail.com  
**Versión:** 2.0 - Enero 2026

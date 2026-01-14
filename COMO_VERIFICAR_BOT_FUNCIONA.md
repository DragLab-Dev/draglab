# 🔍 Cómo Verificar que tu Bot está Funcionando

## 📋 Resumen Rápido

Para asegurarte de que tu bot de señales está escaneando el mercado y enviando señales correctamente, tienes **4 métodos de verificación**:

1. ✅ **Botón "Verificar Ahora"** - Fuerza un escaneo inmediato
2. 📊 **Historial de Señales** - Ver todas las señales enviadas
3. 🟢 **Indicadores de Estado en Tiempo Real** - Monitoreo continuo
4. 📱 **Telegram** - Mensajes directos en tu chat

---

## 1️⃣ Verificación Inmediata: Botón "Verificar Ahora"

### ¿Para qué sirve?
Te permite **forzar una verificación del mercado inmediatamente** sin esperar al próximo ciclo automático del bot.

### ¿Cómo usarlo?
1. Ve a la sección **"3. Mis Bots de Señales"**
2. Encuentra el bot que quieres verificar (debe estar **🟢 ACTIVO**)
3. Haz clic en el botón **🔍 Verificar Ahora**
4. El bot escaneará el mercado **en ese mismo momento**
5. Recibirás un mensaje confirmando:
   - ✅ Si la verificación fue exitosa
   - 🕒 Hora exacta de la última verificación
   - 📡 Si se envió una señal (aparecerá en Telegram si las condiciones se cumplieron)

### ¿Qué significa el resultado?
- **"Market checked successfully"** = El bot está funcionando correctamente
- **"If conditions were met, a signal was sent"** = Si tu estrategia detectó una oportunidad, ya se envió la señal a Telegram
- **"Bot is not running"** = El bot no está activo en el servidor, necesitas activarlo primero

---

## 2️⃣ Historial de Señales

### ¿Para qué sirve?
Ver **todas las señales que tu bot ha enviado** con detalles completos.

### ¿Cómo acceder?
1. En la tarjeta de tu bot, haz clic en **📊 Historial**
2. Verás una ventana con:
   - **Estado actual del bot** (activo/pausado, tiempo activo, última verificación)
   - **Lista completa de señales** ordenadas por fecha
   - **Detalles de cada señal**:
     - 🟢 **ENTRADA LONG** - Señal de compra
     - 🔴 **ENTRADA SHORT** - Señal de venta
     - ⚪ **SALIDA** - Cerrar posición
     - 💰 **Precio** al momento de la señal
     - 🕒 **Fecha y hora** exacta

### Interpretación
- **Muchas señales** = Tu estrategia es muy activa
- **Pocas señales** = Tu estrategia es más conservadora
- **Sin señales** = Las condiciones del mercado aún no han cumplido tu estrategia

---

## 3️⃣ Indicadores en Tiempo Real

### En cada tarjeta de bot verás:

#### 🟢 Estado
- **🟢 ACTIVO** = Bot escaneando el mercado cada X minutos
- **⏸️ PAUSADO** = Bot detenido, no escanea

#### 📊 Estadísticas en Vivo
```
┌─────────────────────┬─────────────────┬─────────────────┐
│ Señales Enviadas    │ Tiempo Activo   │ Última Señal    │
│       5             │      2h         │    15min        │
└─────────────────────┴─────────────────┴─────────────────┘
```

- **Señales Enviadas**: Contador total de señales desde que lo activaste
- **Tiempo Activo**: Cuánto tiempo lleva el bot ejecutándose
- **Última Señal**: Hace cuánto envió la última señal

#### 📡 Última Señal Enviada
Se muestra el **mensaje completo** de la última señal enviada, tal como apareció en Telegram.

---

## 4️⃣ Verificación en Telegram

### Configuración Inicial
Antes de activar el bot, asegúrate de:
1. Tener un **Bot Token** válido de Telegram
2. Tener tu **Chat ID** configurado
3. **Probar la conexión** con el botón "📤 Enviar Mensaje de Prueba"

### ¿Qué mensajes recibirás?

#### Al Activar el Bot
```
🤖 Bot 'Mi Bot BTC' iniciado
📊 Monitoreando BTCUSDT en 15m
```

#### Cuando Detecta una Señal
```
🟢 ENTRADA LONG
━━━━━━━━━━━━━━━━
📊 Par: BTCUSDT
💰 Precio: $42,350.00
⏰ Hora: 14:32:15
━━━━━━━━━━━━━━━━
📈 Condiciones de entrada alcista detectadas
```

---

## ⚠️ Solución de Problemas

### ❌ El bot no envía señales

**Posibles causas:**

1. **El bot está pausado**
   - Solución: Actívalo con el botón **▶️ Activar**

2. **Las condiciones de tu estrategia no se cumplen**
   - Solución: Usa **🔍 Verificar Ahora** para forzar un chequeo
   - Las señales solo se envían cuando el mercado cumple TUS condiciones

3. **Bot Token o Chat ID incorrectos**
   - Solución: Edita el bot (✏️) y usa **"Obtener Chat ID"** y **"Enviar Mensaje de Prueba"**

4. **El servidor no está corriendo**
   - Solución: Verifica que `python app.py` esté ejecutándose
   - Revisa la consola del servidor para ver logs

### ⏰ ¿Cada cuánto verifica el bot?

El bot verifica según el **Intervalo de Tiempo** que configuraste:
- **15m (15 minutos)** → Verifica cada 15 minutos
- **1h (1 hora)** → Verifica cada hora
- **4h (4 horas)** → Verifica cada 4 horas
- **1d (1 día)** → Verifica una vez al día

**TIP**: Usa **🔍 Verificar Ahora** si no quieres esperar al próximo ciclo automático.

### 🔄 ¿Cómo sé si el bot está "vivo"?

**Señales de que tu bot está funcionando:**
1. **Tiempo Activo aumenta** cada minuto
2. **Última Señal** se actualiza cuando hay oportunidades
3. **Puedes usar "Verificar Ahora"** sin errores
4. **En los logs del servidor** ves mensajes como:
   ```
   ✅ Bot Mi Bot BTC started for BTCUSDT on 15m
   🔍 Checking signals for BTCUSDT...
   ```

---

## 🎯 Checklist de Verificación Completa

Usa esta lista para confirmar que todo funciona:

- [ ] Bot está en estado **🟢 ACTIVO**
- [ ] **Tiempo Activo** aumenta constantemente
- [ ] Hice clic en **🔍 Verificar Ahora** y obtuve respuesta exitosa
- [ ] Revisé **📊 Historial** y veo la información del bot
- [ ] **Probé Telegram** y recibo el mensaje de prueba
- [ ] El **intervalo de verificación** está configurado correctamente
- [ ] La **estrategia** tiene bloques en al menos una condición (Entry Long/Short o Exit)

---

## 💡 Tips Profesionales

### 1. Monitoreo Activo
- Deja abierta la página de Signal Bot
- El sistema actualiza las estadísticas cada 5 segundos automáticamente
- Verás cambios en tiempo real

### 2. Prueba con Estrategias Simples Primero
- Crea un bot de prueba con condiciones muy simples
- Ejemplo: "Precio > 40000" para BTC
- Así confirmas que el sistema funciona antes de usar estrategias complejas

### 3. Usa Timeframes Cortos para Pruebas
- Durante pruebas, usa **1m o 5m**
- Verás resultados más rápido
- Luego cambia a timeframes más largos para trading real

### 4. Revisa los Logs del Servidor
En la terminal donde ejecutas `python app.py` verás:
```
✅ Bot Mi Bot BTC started for BTCUSDT on 15m
🔍 Checking signals for BTCUSDT...
📊 Market data fetched: 100 candles
🟢 LONG signal sent for BTCUSDT at $42350.0
```

---

## 📞 ¿Necesitas Más Ayuda?

Si después de seguir todos estos pasos tu bot aún no funciona:

1. **Revisa los logs** en la terminal del servidor
2. **Verifica que la tabla `signal_bots` existe** en la base de datos
3. **Ejecuta** `python update_signal_bots_db.py` si hay errores de base de datos
4. **Reinicia el servidor** (`python app.py`)

---

## 🎉 Conclusión

Con estas 4 herramientas de verificación, siempre sabrás:
- ✅ Si tu bot está activo
- ✅ Cuándo fue la última vez que escaneó el mercado
- ✅ Qué señales ha enviado
- ✅ Si hay algún problema de configuración

**¡Tu bot está diseñado para ser transparente y fácil de monitorear!** 🚀

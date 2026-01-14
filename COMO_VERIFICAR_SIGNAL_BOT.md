# 🔍 Cómo Verificar que Signal Bot Está Funcionando

## 📋 Checklist Completo

### ✅ 1. Verificar que el Servidor Está Ejecutándose

```powershell
# Asegúrate de tener el servidor corriendo
python app.py
```

**Deberías ver:**
```
 * Running on http://127.0.0.1:5000
 * Restarting with stat
 * Debugger is active!
```

---

### ✅ 2. Verificar la Interfaz Web

1. **Abre el navegador** en `http://localhost:5000/signal-bot`
2. **Crea una estrategia** arrastrando bloques
3. **Haz clic en "Crear Bot"** y llena el formulario
4. **Guarda el bot**

**En "My Signal Bots" deberías ver:**
- 🟢 **Conectado al servidor** (texto verde) ✅
- 🔴 **Solo local - Servidor no conectado** (texto rojo) ❌

---

### ✅ 3. Activar el Bot

**Haz clic en "▶️ Activar"**

**Resultado esperado:**
- Si el servidor está corriendo: ✅ "Bot activado correctamente"
- Si el servidor NO está corriendo: ⚠️ "Bot activado (SOLO LOCAL)"

---

### ✅ 4. Verificar Estado del Bot

**Haz clic en el botón "🔄 Verificar"**

Este botón te dirá:
- ✅ Si el servidor está conectado
- 📊 Cuántas señales ha enviado
- ⏰ Cuándo fue la última señal
- 🟢 Si está activo y monitoreando

**Mensajes posibles:**

#### ✅ TODO OK:
```
✅ SERVIDOR CONECTADO

📊 Estado del Bot:
• Status: active
• Señales enviadas: 3
• Última señal: 08/01/2026 14:30:15

🟢 El bot está activo y monitoreando el mercado
```

#### ❌ SERVIDOR NO RESPONDE:
```
🔴 NO SE PUEDE CONECTAR AL SERVIDOR

⚠️ El bot está guardado localmente pero el servidor no está respondiendo.

📋 Para que envíe señales reales:
1. Asegúrate que app.py esté ejecutándose
2. Verifica que no haya errores en la consola del servidor
3. Intenta activar el bot nuevamente
```

---

### ✅ 5. Ver Logs en el Servidor

**En la terminal donde ejecutas `python app.py`, deberías ver:**

```
[2026-01-08 14:30:15] 🤖 Bot "Mi Bot BTC" - Checking market...
[2026-01-08 14:30:15] 📊 BTCUSDT: $95,234.56
[2026-01-08 14:30:15] ✅ Entry LONG condition met!
[2026-01-08 14:30:15] 📨 Sending signal to Telegram...
[2026-01-08 14:30:16] ✅ Signal sent successfully
```

---

### ✅ 6. Ver Señales en Telegram

1. **Abre tu chat con el bot de Telegram**
2. **Espera** (el bot revisa según el intervalo configurado, ej: cada 60 segundos)
3. **Deberías recibir mensajes como:**

```
🟢 SEÑAL DE ENTRADA LONG

📊 Par: BTCUSDT
💰 Precio: $95,234.56
⏰ Hora: 08/01/2026 14:30:15

📈 Condiciones cumplidas:
• Precio > EMA(50)
• RSI(14) < 70

🤖 Bot: Mi Bot BTC
```

---

## 🔧 Solución de Problemas

### ❓ "El bot dice que está activo pero no envía señales"

**Posibles causas:**

1. **Las condiciones no se cumplen aún**
   - El mercado debe cumplir TODAS las condiciones de tu estrategia
   - Espera más tiempo

2. **El Bot Token o Chat ID es incorrecto**
   - Verifica en el formulario del bot
   - Prueba el botón "📨 Enviar Test" antes de activar

3. **El servidor se detuvo**
   - Revisa la terminal donde ejecutaste `python app.py`
   - Busca errores en rojo

4. **Error en la estrategia**
   - Asegúrate de tener bloques en "Entry LONG" o "Entry SHORT"
   - Verifica que los parámetros sean correctos (ej: periodo de EMA debe ser > 0)

---

### ❓ "Aparece 🔴 Solo local - Servidor no conectado"

**Solución:**

1. Verifica que `app.py` esté ejecutándose:
   ```powershell
   python app.py
   ```

2. Verifica que no haya errores en la consola

3. Abre `http://localhost:5000` en el navegador para confirmar

4. Haz clic en "🔄 Verificar" para reconectar

---

### ❓ "El contador de señales no aumenta"

**Esto significa que las condiciones de tu estrategia NO se han cumplido aún.**

**Para probar que funciona:**

1. Crea una estrategia MUY SIMPLE que siempre se cumpla:
   - Entry LONG: `Precio > Número (1000)`
   - (Solo arrastra esos 3 bloques)

2. Activa el bot

3. Espera 1-2 minutos

4. Deberías recibir señales constantemente (porque el precio de Bitcoin siempre es > $1000)

---

## 📊 Interpretación de los Indicadores

### 🟢 Conectado al servidor
- ✅ El backend está funcionando
- ✅ El bot puede enviar señales a Telegram
- ✅ Las estadísticas se actualizan en tiempo real

### 🔴 Solo local
- ❌ El bot NO enviará señales reales
- ❌ Solo está guardado en tu navegador
- ⚠️ Necesitas ejecutar `python app.py`

### Señales: 0 / 5 / 10...
- Número de señales enviadas a Telegram
- Se incrementa cada vez que envía un mensaje

### Tiempo Activo: 1h / 2d / 3w...
- Tiempo total que el bot ha estado activo
- Se reinicia si pausas y reactivas

### Última Señal: Ahora / 5min / 2h...
- Tiempo desde la última señal enviada
- "-" = nunca ha enviado señales

---

## 🎯 Ejemplo de Flujo Completo

```
1. ✅ python app.py ejecutándose
2. ✅ Navegador abierto en http://localhost:5000/signal-bot
3. ✅ Estrategia creada con bloques
4. ✅ Bot creado con Token y Chat ID correctos
5. ✅ Mensaje de prueba enviado correctamente (📨 Enviar Test)
6. ✅ Bot activado (▶️ Activar)
7. ✅ Indicador muestra "🟢 Conectado al servidor"
8. ✅ Click en "🔄 Verificar" muestra status activo
9. ⏳ Esperar a que se cumplan las condiciones
10. 📨 Recibir señal en Telegram
11. 📊 Contador de señales aumenta de 0 a 1
```

---

## 💡 Tips

- **Usa el botón "🔄 Verificar"** cada 30 segundos para ver el estado actualizado
- **Revisa la consola del servidor** (`python app.py`) para ver logs en tiempo real
- **Empieza con estrategias simples** para probar que todo funciona
- **Usa intervalos cortos** (30-60 segundos) al principio para ver resultados rápido
- **Ten Telegram abierto** para ver las señales inmediatamente

---

## 🚨 Si NADA Funciona

1. **Detén todo:**
   ```powershell
   # Presiona Ctrl+C en la terminal donde corre app.py
   ```

2. **Verifica dependencias:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Reinicia el servidor:**
   ```powershell
   python app.py
   ```

4. **Recarga la página del navegador** (Ctrl+F5)

5. **Crea un bot nuevo** con una estrategia simple

6. **Haz clic en "🔄 Verificar"** para confirmar conexión

---

## ✅ Checklist Final

- [ ] `python app.py` ejecutándose sin errores
- [ ] Navegador en `http://localhost:5000/signal-bot`
- [ ] Bot creado con todos los campos llenos
- [ ] Botón "📨 Enviar Test" funciona
- [ ] Bot activado (status: ✅ Activo)
- [ ] Indicador muestra "🟢 Conectado al servidor"
- [ ] Botón "🔄 Verificar" responde correctamente
- [ ] Telegram abierto esperando señales

**Si todos están ✅, ¡tu bot está funcionando correctamente!**

---

## 📞 Soporte

Si después de seguir todos estos pasos aún no funciona:

1. Copia los logs de la consola del servidor
2. Toma capturas de pantalla de los errores
3. Copia el contenido de la consola del navegador (F12)
4. Contacta para soporte técnico

---

**Creado por:** camiloeagiraldodev@gmail.com

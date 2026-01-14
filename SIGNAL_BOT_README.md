# Signal Bot - Sistema Completo de Bots de Trading

## 🎯 Descripción

Signal Bot es un sistema completo para crear y gestionar bots de trading que envían señales automáticas a Telegram basadas en estrategias personalizadas creadas mediante bloques visuales.

## 🏗️ Arquitectura del Sistema

### Backend (Python/Flask)

#### 1. **Base de Datos** (`database.py`)
- Gestión de usuarios y autenticación
- Almacenamiento de configuraciones de bots
- Historial de señales enviadas

**Tablas principales:**
- `signal_bots`: Configuración de cada bot
- `bot_signals`: Historial de señales enviadas
- `users`: Gestión de usuarios

#### 2. **API Routes** (`signal_bot_routes.py`)

**Endpoints de Bots:**
- `POST /api/signal-bots/create` - Crear nuevo bot
- `GET /api/signal-bots/list` - Listar bots del usuario
- `GET /api/signal-bots/get/<bot_id>` - Obtener info de un bot
- `PUT /api/signal-bots/update/<bot_id>` - Actualizar bot
- `DELETE /api/signal-bots/delete/<bot_id>` - Eliminar bot
- `POST /api/signal-bots/activate/<bot_id>` - Activar bot
- `POST /api/signal-bots/pause/<bot_id>` - Pausar bot
- `GET /api/signal-bots/logs/<bot_id>` - Ver historial de señales
- `GET /api/signal-bots/health` - Estado del sistema

**Endpoints de Telegram:**
- `POST /api/telegram/get-chat-id` - Obtener Chat ID de Telegram
- `POST /api/telegram/send-test` - Enviar mensaje de prueba

#### 3. **Bot Engine** (`bot_engine.py`)

Motor que ejecuta los bots en hilos separados:
- **TradingBot**: Clase que representa un bot individual
  - Monitorea el mercado cada X segundos
  - Evalúa estrategias de entrada/salida
  - Envía señales a Telegram cuando se cumplen condiciones
  
- **BotEngine**: Gestor de múltiples bots
  - Inicia, detiene y reinicia bots
  - Mantiene estado de todos los bots activos
  - Thread-safe para operaciones concurrentes

#### 4. **Market Data Provider** (`market_data.py`)
- Obtiene datos en tiempo real de Binance
- Calcula indicadores técnicos (EMA, SMA, RSI, MACD, etc.)
- Sistema de caché para optimizar requests

#### 5. **Strategy Evaluator** (`strategy_evaluator.py`)
- Evalúa estrategias creadas con bloques visuales
- Soporta indicadores, operadores de comparación y lógica
- Genera mensajes formateados para Telegram

#### 6. **Telegram Sender** (`telegram_sender.py`)
- Envía mensajes a Telegram usando Bot API
- Soporte para HTML y Markdown
- Manejo de errores y reintentos

### Frontend (HTML/JavaScript)

#### Constructor Visual de Estrategias
- Paleta de bloques drag-and-drop
- 4 zonas de estrategia: Entry/Exit Long/Short
- Vista previa de estrategia en tiempo real
- Export/Import de estrategias en JSON

#### Panel de Administración de Bots
- Crear, editar y eliminar bots
- Activar/pausar bots
- Ver estadísticas en tiempo real
- Historial de señales

#### Integración con Telegram
- Obtener Chat ID automáticamente
- Enviar mensajes de prueba
- Configuración de Bot Token

## 🚀 Instalación y Configuración

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2. Inicializar Base de Datos

```bash
python update_signal_bots_db.py
```

Este script crea las tablas necesarias:
- `signal_bots` - Configuración de bots
- `bot_signals` - Historial de señales

### 3. Configurar Telegram Bot

1. Habla con [@BotFather](https://t.me/BotFather) en Telegram
2. Crea un nuevo bot con `/newbot`
3. Copia el **Bot Token** que te proporciona
4. Envía un mensaje a tu bot para activarlo
5. Usa el sistema para obtener tu **Chat ID**

### 4. Ejecutar la Aplicación

```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5000`

## 📋 Uso del Sistema

### Crear una Estrategia

1. **Accede a Signal Bot** desde el menú principal
2. **Arrastra bloques** desde la paleta a las zonas de estrategia
3. **Configura parámetros** de cada bloque (períodos, valores, etc.)
4. **Vista previa** de la estrategia se actualiza automáticamente

**Ejemplo de estrategia simple:**
```
Entry Long:
  - Precio > EMA(50)
  - RSI(14) < 70

Exit Long:
  - Precio < EMA(50)
  - RSI(14) > 70
```

### Crear un Bot

1. **Completa tu estrategia** en el constructor visual
2. Haz clic en **"Crear Nuevo Bot"**
3. Completa el formulario:
   - **Nombre**: Identifica tu bot
   - **Bot Token**: Token de Telegram Bot
   - **Chat ID**: ID del chat donde recibir señales
   - **Symbol**: Par de trading (ej: BTCUSDT)
   - **Timeframe**: Intervalo de tiempo (1m, 5m, 15m, 1h, 4h, 1d)
   - **Check Interval**: Segundos entre verificaciones (mín: 60)
4. **Prueba la conexión** con "Obtener Chat ID" y "Enviar Prueba"
5. Haz clic en **"Guardar Bot"**

### Activar un Bot

1. Localiza tu bot en la lista
2. Haz clic en **"▶ Activar"**
3. El bot comenzará a monitorear el mercado
4. Recibirás señales en Telegram cuando se cumplan las condiciones

### Gestionar Bots

- **✏️ Editar**: Modificar configuración o estrategia
- **⏸️ Pausar**: Detener temporalmente el bot
- **📊 Historial**: Ver señales enviadas
- **🗑️ Eliminar**: Borrar bot permanentemente

## 🔧 Estructura de Datos

### Configuración de Bot (JSON)

```json
{
  "id": "bot_123456789",
  "name": "BTC Trend Bot",
  "bot_token": "123456:ABC-DEF...",
  "chat_id": "987654321",
  "symbol": "BTCUSDT",
  "timeframe": "15m",
  "check_interval": 60,
  "strategy": {
    "entry_long": [...],
    "exit_long": [...],
    "entry_short": [...],
    "exit_short": [...]
  },
  "status": "active",
  "signals_sent": 42,
  "uptime": 3600
}
```

### Bloque de Estrategia (JSON)

```json
{
  "type": "indicator",
  "name": "EMA",
  "params": {
    "period": 50,
    "price": "close"
  }
}
```

## 📊 Tipos de Bloques

### Indicadores Técnicos
- **EMA** - Media Móvil Exponencial
- **SMA** - Media Móvil Simple
- **RSI** - Índice de Fuerza Relativa
- **MACD** - Convergencia/Divergencia
- **Bollinger** - Bandas de Bollinger
- **ATR** - Rango Verdadero Promedio
- **Swing** - Máximos/Mínimos Locales

### Valores
- **Precio** - Precio actual del mercado
- **Número** - Valor numérico fijo
- **Porcentaje** - Valor porcentual

### Operadores de Comparación
- **> < >= <= == !=** - Comparaciones estándar
- **Cruza (✖)** - Detecta cruces de líneas

### Operadores Lógicos
- **AND** - Ambas condiciones verdaderas
- **OR** - Al menos una condición verdadera
- **NOT** - Negación
- **XOR** - Solo una condición verdadera
- **NAND/NOR** - Operadores lógicos avanzados

## 🔐 Seguridad

- ✅ Autenticación de usuarios requerida
- ✅ Tokens de Telegram nunca se muestran en logs
- ✅ Cada usuario solo ve sus propios bots
- ✅ Validación de datos en frontend y backend
- ✅ Protección contra SQL injection
- ✅ Rate limiting en APIs externas

## 📈 Monitoreo y Estadísticas

Cada bot muestra en tiempo real:
- **Estado**: Activo/Pausado
- **Señales Enviadas**: Contador total
- **Tiempo Activo**: Uptime del bot
- **Última Señal**: Timestamp y tipo
- **Symbol/Timeframe**: Configuración actual

## 🐛 Solución de Problemas

### Bot no envía señales

1. Verifica que el bot esté **Activo** (estado verde)
2. Comprueba que el **Bot Token** sea válido
3. Verifica que el **Chat ID** sea correcto
4. Asegúrate de que la estrategia tenga bloques configurados
5. Revisa los logs del servidor para errores

### No puedo obtener Chat ID

1. Envía **/start** a tu bot en Telegram
2. Envía cualquier mensaje al bot
3. Espera unos segundos
4. Intenta obtener el Chat ID nuevamente

### Señales no llegan a Telegram

1. Verifica que el bot no esté bloqueado
2. Comprueba que el Chat ID sea correcto
3. Prueba con "Enviar Mensaje de Prueba"
4. Revisa la consola del servidor para errores

### Bot se detiene inesperadamente

1. Revisa los logs del servidor
2. Verifica la conexión a internet
3. Comprueba que Binance API esté disponible
4. Asegúrate de que no hay errores en la estrategia

## 🔄 Flujo de Ejecución de un Bot

1. **Inicio**: Bot se activa desde el frontend
2. **Backend**: Crea instancia de TradingBot
3. **Loop Principal**: Cada X segundos:
   - Obtiene datos del mercado (Binance)
   - Calcula indicadores necesarios
   - Evalúa condiciones de entrada/salida
   - Si se cumple condición → Envía señal a Telegram
4. **Actualización**: Guarda estadísticas en DB
5. **Detención**: Al pausar, termina el thread limpiamente

## 📝 API Reference

### POST /api/signal-bots/create

Crea un nuevo bot de señales.

**Request Body:**
```json
{
  "name": "Mi Bot",
  "bot_token": "123:ABC",
  "chat_id": "123456",
  "symbol": "BTCUSDT",
  "timeframe": "15m",
  "check_interval": 60,
  "strategy": { ... }
}
```

**Response:**
```json
{
  "success": true,
  "bot_id": 1,
  "message": "Bot created successfully"
}
```

### POST /api/telegram/get-chat-id

Obtiene el Chat ID de un bot de Telegram.

**Request Body:**
```json
{
  "bot_token": "123:ABC"
}
```

**Response:**
```json
{
  "success": true,
  "chat_id": "123456",
  "message": "Chat ID obtained successfully"
}
```

## 🌟 Características Avanzadas

### Export/Import de Estrategias
- Exporta estrategias como archivos JSON
- Importa estrategias creadas previamente
- Comparte estrategias con otros usuarios

### Modo Oscuro
- Interfaz adaptable al tema del sistema
- Mejor visibilidad en condiciones de poca luz

### Multilenguaje
- Soporte para Español e Inglés
- Cambio dinámico sin recargar

### Almacenamiento Local
- Bots guardados en localStorage como backup
- Funcionalidad offline limitada
- Sincronización automática con el servidor

## 📚 Recursos Adicionales

- **Binance API Docs**: https://binance-docs.github.io/apidocs/spot/en/
- **Telegram Bot API**: https://core.telegram.org/bots/api
- **TradingView**: https://www.tradingview.com/ (para análisis técnico)

## 🤝 Contribuciones

Creado por **camiloeagiraldodev@gmail.com**

## ⚖️ Disclaimer Legal

⚠️ **IMPORTANTE**: Este software es únicamente con fines educativos y de prueba.

- ❌ NO es asesoramiento financiero profesional
- ❌ NO garantiza rendimientos futuros
- ❌ Los resultados pasados NO predicen resultados futuros
- ✅ El trading conlleva riesgo de pérdida de capital
- ✅ Usa este software bajo tu propia responsabilidad

---

**Versión**: 2.0  
**Fecha**: Enero 2026  
**Licencia**: Uso Personal

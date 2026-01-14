# DragLab

> **Constructor Visual de Estrategias de Trading mediante Bloques - Sin Necesidad de Programar**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-Private-red.svg)]()

**Desarrollado por:** camiloeagiraldodev@gmail.com | **Versión:** 2.4 | **Fecha:** Enero 2026

---

## 🎯 ¿Qué es Draglab?

Plataforma revolucionaria que permite a **cualquier persona** crear estrategias de trading y bots automatizados **sin escribir una sola línea de código**. Mediante un sistema de **bloques visuales** tipo drag-and-drop, puedes diseñar, probar y ejecutar estrategias profesionales de trading.

### 💡 El Valor Diferencial

- **🧩 Constructor de Bloques Visual**: Arrastra y conecta bloques para crear estrategias complejas
- **🚫 Sin Programación**: No necesitas saber Python, JavaScript ni ningún lenguaje
- **📊 Backtest Integrado**: Prueba tus estrategias con datos históricos reales
- **🤖 Creación de Bots**: Convierte tus estrategias en bots de trading automatizados
- **👥 Accesible para Todos**: Desde principiantes hasta traders expertos

---

## 📋 Características Principales

✅ **Visual Strategy Builder**: Sistema drag-and-drop con bloques para diseñar estrategias sin código  
✅ **Bloques Pre-Configurados**: Indicadores técnicos, condiciones, señales de entrada/salida  
✅ **Backtest Profesional**: Ejecuta backtests con datos históricos de Binance  
✅ **Creación de Bots**: Transforma estrategias visuales en bots automatizados  
✅ **Descarga de Datos**: Obtención automática OHLCV desde Binance  
✅ **Sistema de Autenticación**: Login con email + verificación o Google OAuth  
✅ **Panel de Administración**: Gestión de usuarios y suscripciones  
✅ **Gráficos Interactivos**: Visualización avanzada con Bokeh  
✅ **Soporte Bilingüe**: Español e Inglés  
✅ **Import/Export**: Guarda y comparte tus estrategias en JSON  

---

## 🚀 Inicio Rápido

### Desarrollo Local (Windows)

```cmd
# 1. Clonar repositorio
git clone <url-del-repositorio>
cd "Visual strategy creator"

# 2. Instalar automáticamente
install.bat

# 3. Configurar variables
copy .env.example .env
# Editar .env con tus credenciales

# 4. Iniciar aplicación
start.bat
```

### Desarrollo Local (Linux/Mac)

```bash
# 1. Clonar repositorio
git clone <url-del-repositorio>
cd visual-strategy-creator

# 2. Instalar automáticamente
chmod +x install.sh
./install.sh

# 3. Configurar variables
cp .env.example .env
nano .env  # Editar credenciales

# 4. Iniciar aplicación
./start.sh
```

**Aplicación disponible en:** http://localhost:5000

---

## 📦 Configuración de .env

Variables **obligatorias** en `.env`:

```bash
# Generar con: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=tu-clave-secreta-aqui

# Configurar en https://myaccount.google.com/apppasswords
GMAIL_USER=tu-email@gmail.com
GMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx

# Opcional: Google OAuth (https://console.cloud.google.com/)
GOOGLE_CLIENT_ID=tu-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=tu-client-secret
```

---

## 🌐 Despliegue en VPS

Ver documentación completa en **[DEPLOYMENT.md](DEPLOYMENT.md)**

**Resumen rápido:**

```bash
# En tu VPS
git clone <url-del-repositorio>
cd visual-strategy-creator
./install.sh
nano .env  # Configurar variables
./start.sh
```

Para producción con NGINX y SSL, consulta [DEPLOYMENT.md](DEPLOYMENT.md)

---

## � Estructura del Proyecto

```
visual-strategy-creator/
├── app.py                 # Aplicación Flask principal
├── database.py            # Gestión de base de datos SQLite
├── auth_routes.py         # Autenticación (email/Google)
├── admin_routes.py        # Panel administrativo
├── payments_routes.py     # Suscripciones y pagos
├── google_auth.py         # Google OAuth
├── email_service.py       # Envío de emails
├── requirements.txt       # Dependencias Python
├── .env.example           # Plantilla de variables de entorno
├── README.md              # Este archivo
├── DEPLOYMENT.md          # Guía de despliegue VPS
├── templates/             # Plantillas HTML
├── database/              # Base de datos SQLite
└── data/                  # Datos históricos CSV
```

---

## 💡 Cómo Usar la Aplicación

### 1️⃣ Autenticación
1. Accede a http://localhost:5000/welcome
2. Regístrate con email o Google OAuth
3. Verifica con código de 4 dígitos (si usas email)

### 2️⃣ Visual Strategy Builder (Sin Programar)

**El corazón de la aplicación** - Crea estrategias arrastrando bloques:

- 🧱 **Bloques de Indicadores**: EMA, SMA, RSI, MACD, Bollinger Bands, ATR, Swing High/Low
- 🔗 **Bloques de Condiciones**: >, <, =, >=, <=, AND, OR
- 📥 **Bloques de Señales**: Entrada Long/Short, Salida, Stop Loss, Take Profit
- 🎯 **Drag & Drop**: Arrastra bloques, conéctalos y crea estrategias complejas
- 💾 **Import/Export**: Guarda tus estrategias visuales en formato JSON
- 🚫 **Sin Código**: Todo es visual - no necesitas saber programar

### 3️⃣ Backtest de tu Estrategia
1. Descarga datos históricos desde Binance
2. Configura tu estrategia en el constructor de bloques
3. Ajusta parámetros (capital inicial, comisiones, etc.)
4. Ejecuta backtest y analiza resultados gráficos

### 4️⃣ Creación de Bots de Trading
- Convierte tu estrategia visual en un bot automatizado
- El bot ejecutará las señales según tu diseño de bloques
- Monitoreo en tiempo real

### 5️⃣ Panel Admin (Solo Administradores)
- Gestión de usuarios y roles
- Control de suscripciones
- Estadísticas del sistema
- Acceso: usuarios con rol `admin`

---

## 🔒 Seguridad

### Variables de Entorno Críticas

```bash
# NUNCA subas a Git:
- .env
- database/tradingbot.db
- Credenciales de API
```

### Mejores Prácticas

✅ Usa contraseñas fuertes  
✅ Habilita HTTPS en producción  
✅ Configura firewall (UFW)  
✅ Actualiza dependencias regularmente  
✅ Haz backups de la base de datos  

---

## 🐛 Solución de Problemas

### Error: "Module not found"
```bash
pip install -r requirements.txt
```

### Error: "Database locked"
```bash
# Verifica que no haya múltiples instancias corriendo
pkill -f "python app.py"
```

### Error de autenticación Gmail
```bash
# Genera App Password en Google:
# https://myaccount.google.com/apppasswords
```

---

## 📞 Soporte

**Desarrollador:** camiloeagiraldodev@gmail.com

**Reportar bugs:** Crea un issue en el repositorio

**Documentación adicional:** Ver archivos `.md` en el proyecto

---

## 📜 Licencia

Este� Gestión de Usuarios

### Crear Usuario Admin

```bash
python3 << EOF
import database as db
db.init_database()
db.create_user("admin@tudominio.com", "ContraseñaSegura123!", is_admin=True)
print("Admin creado exitosamente")
EOF
```

### Roles
- **user** - Acceso a backtest y constructor
- **admin** - Panel de administración + gestión de usuarios

---

## 🔒 Seguridad

**Archivos excluidos de Git** (ver `.gitignore`):
- `.env` - Variables de entorno
- `database/*.db` - Base de datos
- `data/*.csv` - Datos históricos

**Mejores prácticas:**
- Usa contraseñas fuertes (mín. 8 caracteres)
- Habilita HTTPS en producción (Let's Encrypt)
- Configura firewall: `sudo ufw allow 80,443/tcp`
- Backups regulares de `database/tradingbot.db`

---

## 🐛 Solución de Problemas

| Error | Solución |
|-------|----------|
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
| `Database is locked` | `pkill -f gunicorn` o `pkill -f "python app.py"` |
| Gmail auth error | Genera App Password en https://myaccount.google.com/apppasswords |
| Port 5000 already in use | Cambia `PORT` en `.env` o mata proceso: `lsof -ti:5000 \| xargs kill` |

---

## 📞 Soporte y Contacto

**Desarrollador:** camiloeagiraldodev@gmail.com  
**Versión:** 2.4 (Enero 2026)  
**Documentación adicional:** [DEPLOYMENT.md](DEPLOYMENT.md)Proyecto de uso privado. Todos los derechos reservados © 2026

---

## 🔄 Actualizaciones

Para actualizar el proyecto en VPS:

```bash
cd /ruta/al/proyecto
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart visualstrategy
```

---

**Visual Strategy Creator v2.4** - Plataforma profesional de backtesting de estrategias de trading

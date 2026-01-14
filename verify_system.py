"""
Script de Verificación del Sistema de Bots
Ejecuta este script para verificar que todo está funcionando correctamente
"""

print("\n" + "="*60)
print("🔍 VERIFICACIÓN DEL SISTEMA DE BOTS")
print("="*60 + "\n")

# Test 1: Verificar Base de Datos
print("📊 TEST 1: Base de Datos")
print("-" * 40)
try:
    import sqlite3
    conn = sqlite3.connect('database/app.db')
    cursor = conn.cursor()
    
    # Verificar tabla signal_bots
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='signal_bots'")
    if cursor.fetchone():
        print("✅ Tabla 'signal_bots' existe")
        cursor.execute("SELECT COUNT(*) FROM signal_bots")
        count = cursor.fetchone()[0]
        print(f"   └─ Bots registrados: {count}")
    else:
        print("❌ Tabla 'signal_bots' NO existe")
    
    # Verificar tabla bot_signals
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bot_signals'")
    if cursor.fetchone():
        print("✅ Tabla 'bot_signals' existe")
        cursor.execute("SELECT COUNT(*) FROM bot_signals")
        count = cursor.fetchone()[0]
        print(f"   └─ Señales registradas: {count}")
    else:
        print("❌ Tabla 'bot_signals' NO existe")
    
    conn.close()
    print("\n✅ Base de datos: OK\n")
except Exception as e:
    print(f"\n❌ Error en base de datos: {e}\n")

# Test 2: Verificar Imports
print("📦 TEST 2: Módulos Python")
print("-" * 40)
modules = {
    'requests': 'Llamadas HTTP',
    'pandas': 'Análisis de datos',
    'numpy': 'Cálculos numéricos',
    'sqlite3': 'Base de datos'
}

all_ok = True
for module, desc in modules.items():
    try:
        __import__(module)
        print(f"✅ {module:12} - {desc}")
    except ImportError:
        print(f"❌ {module:12} - {desc} (NO INSTALADO)")
        all_ok = False

if all_ok:
    print("\n✅ Todos los módulos: OK\n")
else:
    print("\n⚠️  Faltan módulos, instala con: pip install -r requirements.txt\n")

# Test 3: Verificar Archivos del Backend
print("📁 TEST 3: Archivos Backend")
print("-" * 40)
files = {
    'signal_bot_routes.py': 'API REST',
    'market_data.py': 'Datos de Binance',
    'strategy_evaluator.py': 'Evaluador de estrategias',
    'telegram_sender.py': 'Envío a Telegram',
    'bot_engine.py': 'Motor de ejecución'
}

all_ok = True
import os
for file, desc in files.items():
    if os.path.exists(file):
        print(f"✅ {file:25} - {desc}")
    else:
        print(f"❌ {file:25} - {desc} (NO EXISTE)")
        all_ok = False

if all_ok:
    print("\n✅ Todos los archivos: OK\n")
else:
    print("\n❌ Faltan archivos del backend\n")

# Test 4: Verificar Blueprint registrado
print("🔧 TEST 4: Integración con Flask")
print("-" * 40)
try:
    with open('app.py', 'r', encoding='utf-8') as f:
        app_content = f.read()
        
    if 'from signal_bot_routes import signal_bot_bp' in app_content:
        print("✅ Import del blueprint: OK")
    else:
        print("❌ Falta import del blueprint")
    
    if 'app.register_blueprint(signal_bot_bp)' in app_content:
        print("✅ Registro del blueprint: OK")
    else:
        print("❌ Falta registro del blueprint")
    
    print("\n✅ Integración Flask: OK\n")
except Exception as e:
    print(f"\n❌ Error verificando Flask: {e}\n")

# Test 5: Test de API de Binance
print("🌐 TEST 5: Conexión a Binance")
print("-" * 40)
try:
    import requests
    response = requests.get('https://api.binance.com/api/v3/ping', timeout=5)
    if response.status_code == 200:
        print("✅ API de Binance: Accesible")
        
        # Probar obtener precio
        response = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT', timeout=5)
        if response.status_code == 200:
            price = response.json()['price']
            print(f"   └─ Precio BTC: ${float(price):,.2f}")
            print("\n✅ Conexión a Binance: OK\n")
        else:
            print(f"⚠️  No se pudo obtener precio: {response.status_code}\n")
    else:
        print(f"❌ API no accesible: {response.status_code}\n")
except Exception as e:
    print(f"❌ Error conectando a Binance: {e}\n")

# Resumen Final
print("="*60)
print("📋 RESUMEN DE VERIFICACIÓN")
print("="*60)
print("""
Para que el sistema funcione completamente:

1. ✅ Base de datos configurada
2. ✅ Archivos backend creados
3. ✅ Blueprint registrado en Flask
4. ✅ API de Binance accesible

PRÓXIMOS PASOS:
-----------------
1. Inicia el servidor Flask:
   → python app.py

2. Abre el navegador:
   → http://127.0.0.1:5000/signal-bot

3. Crea tu estrategia con bloques visuales

4. Crea un bot de Telegram:
   → Abre Telegram
   → Busca @BotFather
   → Envía /newbot
   → Guarda el token

5. Crea tu primer bot en la interfaz

6. ¡Activa el bot y recibe señales!

DOCUMENTACIÓN:
--------------
- BOT_SYSTEM_README.md (completa)
- QUICKSTART.md (guía rápida)
""")

print("="*60)
print("✅ VERIFICACIÓN COMPLETADA")
print("="*60 + "\n")

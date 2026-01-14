"""
Script de Inicio Rápido para Signal Bot
Verifica dependencias, inicializa la base de datos y ejecuta la aplicación
"""

import sys
import subprocess
import os
from pathlib import Path

def print_header(text):
    """Imprimir encabezado formateado"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def check_dependencies():
    """Verificar que todas las dependencias estén instaladas"""
    print_header("🔍 Verificando Dependencias")
    
    required_modules = [
        'flask',
        'pandas',
        'numpy',
        'requests',
        'python-dotenv',
        'werkzeug'
    ]
    
    missing = []
    
    for module in required_modules:
        try:
            __import__(module.replace('-', '_'))
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module} - NO ENCONTRADO")
            missing.append(module)
    
    if missing:
        print("\n⚠️  Módulos faltantes detectados.")
        print(f"📦 Instalando: {', '.join(missing)}")
        print()
        
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing)
            print("\n✅ Todas las dependencias instaladas correctamente")
        except subprocess.CalledProcessError:
            print("\n❌ Error instalando dependencias. Instálalas manualmente:")
            print(f"   pip install {' '.join(missing)}")
            return False
    else:
        print("\n✅ Todas las dependencias están instaladas")
    
    return True

def init_database():
    """Inicializar la base de datos"""
    print_header("🗄️  Inicializando Base de Datos")
    
    try:
        # Verificar si las tablas ya existen
        from database import get_db_connection
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='signal_bots'")
        signal_bots_exists = cursor.fetchone() is not None
        conn.close()
        
        if signal_bots_exists:
            print("  ✅ Tablas de Signal Bot ya existen")
            return True
        
        # Ejecutar script de actualización
        print("  📋 Creando tablas de Signal Bot...")
        result = subprocess.run([sys.executable, 'update_signal_bots_db.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("  ✅ Base de datos inicializada correctamente")
            return True
        else:
            print(f"  ❌ Error inicializando base de datos:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def check_env_file():
    """Verificar archivo .env"""
    print_header("🔧 Verificando Configuración")
    
    env_file = Path('.env')
    
    if not env_file.exists():
        print("  ⚠️  Archivo .env no encontrado")
        print("  📝 Creando .env con valores predeterminados...")
        
        with open(env_file, 'w') as f:
            f.write("# Signal Bot Configuration\n")
            f.write("SECRET_KEY=dev-secret-key-change-in-production\n")
            f.write("FLASK_ENV=development\n")
            f.write("# Add your config here\n")
        
        print("  ✅ Archivo .env creado")
        print("  💡 Tip: Modifica .env con tus propias configuraciones")
    else:
        print("  ✅ Archivo .env encontrado")
    
    return True

def start_application():
    """Iniciar la aplicación Flask"""
    print_header("🚀 Iniciando Signal Bot")
    
    print("""
  📡 Signal Bot - Sistema de Trading Automático
  
  ✅ La aplicación se está iniciando...
  🌐 URL: http://localhost:5000
  
  📋 Instrucciones:
     1. Abre http://localhost:5000 en tu navegador
     2. Inicia sesión o regístrate
     3. Ve a "Signal Bot" desde el menú
     4. Crea tu estrategia arrastrando bloques
     5. Configura tu bot de Telegram
     6. ¡Activa el bot y recibe señales!
  
  ⏸️  Presiona Ctrl+C para detener el servidor
    """)
    
    print("="*70)
    print()
    
    try:
        # Importar y ejecutar la aplicación
        from app import app
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\n\n⏹️  Servidor detenido por el usuario")
    except Exception as e:
        print(f"\n❌ Error ejecutando la aplicación: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def main():
    """Función principal"""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("""
    ███████╗██╗ ██████╗ ███╗   ██╗ █████╗ ██╗         ██████╗  ██████╗ ████████╗
    ██╔════╝██║██╔════╝ ████╗  ██║██╔══██╗██║         ██╔══██╗██╔═══██╗╚══██╔══╝
    ███████╗██║██║  ███╗██╔██╗ ██║███████║██║         ██████╔╝██║   ██║   ██║   
    ╚════██║██║██║   ██║██║╚██╗██║██╔══██║██║         ██╔══██╗██║   ██║   ██║   
    ███████║██║╚██████╔╝██║ ╚████║██║  ██║███████╗    ██████╔╝╚██████╔╝   ██║   
    ╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝    ╚═════╝  ╚═════╝    ╚═╝   
    
    Sistema de Trading Automático con Telegram
    Versión 2.0 | Enero 2026
    """)
    
    # Verificar dependencias
    if not check_dependencies():
        print("\n❌ Falló la verificación de dependencias")
        print("   Por favor, instala las dependencias faltantes e intenta nuevamente")
        sys.exit(1)
    
    # Verificar archivo .env
    if not check_env_file():
        print("\n❌ Falló la verificación de configuración")
        sys.exit(1)
    
    # Inicializar base de datos
    if not init_database():
        print("\n❌ Falló la inicialización de la base de datos")
        print("   Intenta ejecutar manualmente: python update_signal_bots_db.py")
        sys.exit(1)
    
    # Iniciar aplicación
    start_application()

if __name__ == '__main__':
    main()

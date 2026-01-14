"""
Script para crear/actualizar las tablas de Signal Bots en la base de datos
Ejecutar este script para preparar la base de datos para Signal Bot
"""

from database import get_db_connection
import sys

def update_signal_bots_tables():
    """Crear o actualizar tablas necesarias para Signal Bot"""
    print("🔧 Actualizando tablas de Signal Bot...")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Tabla de bots de señales
        print("📋 Creando tabla signal_bots...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signal_bots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                bot_token TEXT,
                chat_id TEXT,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                check_interval INTEGER DEFAULT 60,
                strategy TEXT NOT NULL,
                status TEXT DEFAULT 'paused',
                signals_sent INTEGER DEFAULT 0,
                uptime INTEGER DEFAULT 0,
                last_signal REAL,
                last_signal_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Tabla de señales enviadas (historial)
        print("📋 Creando tabla bot_signals...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bot_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bot_id INTEGER NOT NULL,
                signal_type TEXT NOT NULL,
                signal_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (bot_id) REFERENCES signal_bots(id)
            )
        ''')
        
        # Crear índices para mejorar el rendimiento
        print("📊 Creando índices...")
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_signal_bots_user_id 
            ON signal_bots(user_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_signal_bots_status 
            ON signal_bots(status)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_bot_signals_bot_id 
            ON bot_signals(bot_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_bot_signals_created_at 
            ON bot_signals(created_at)
        ''')
        
        conn.commit()
        conn.close()
        
        print("✅ Tablas de Signal Bot creadas/actualizadas exitosamente")
        print("\n📊 Resumen:")
        print("   - signal_bots: Almacena configuración de bots")
        print("   - bot_signals: Almacena historial de señales")
        print("\n🎯 El sistema está listo para crear Signal Bots")
        return True
        
    except Exception as e:
        print(f"❌ Error actualizando base de datos: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_tables():
    """Verificar que las tablas existan y mostrar información"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print("\n📊 Verificación de tablas:")
        
        required_tables = ['signal_bots', 'bot_signals', 'users']
        for table in required_tables:
            if table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"   ✅ {table}: {count} registros")
            else:
                print(f"   ❌ {table}: NO EXISTE")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error verificando tablas: {e}")

if __name__ == '__main__':
    print("=" * 60)
    print("SIGNAL BOT - Database Setup")
    print("=" * 60)
    print()
    
    success = update_signal_bots_tables()
    
    if success:
        verify_tables()
        print("\n" + "=" * 60)
        print("✅ Setup completado exitosamente!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ Setup falló. Revisa los errores arriba.")
        print("=" * 60)
        sys.exit(1)

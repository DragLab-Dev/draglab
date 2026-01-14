"""
Inicializar tablas de suscripciones
Ejecutar este script para crear las tablas necesarias
"""

import sqlite3
import os

def init_subscriptions_db():
    """Crear tablas de suscripciones en la base de datos"""
    
    # Ruta a la base de datos
    db_path = os.path.join('database', 'draglab.db')
    
    if not os.path.exists('database'):
        os.makedirs('database')
    
    print(f"📁 Conectando a base de datos: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("🔧 Creando tabla subscriptions...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                plan_name TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                payment_id TEXT,
                payment_method TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        print("🔧 Creando tabla payments...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                subscription_id INTEGER,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'USD',
                payment_method TEXT NOT NULL,
                payment_id TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT (datetime('now')),
                completed_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (subscription_id) REFERENCES subscriptions(id) ON DELETE SET NULL
            )
        """)
        
        print("🔧 Creando tabla backtest_results...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS backtest_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                strategy TEXT,
                total_trades INTEGER,
                win_rate REAL,
                total_profit REAL,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        print("🔧 Creando tabla strategies...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS strategies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                strategy_data TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        print("🔧 Creando tabla signal_bots...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS signal_bots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                status TEXT DEFAULT 'paused',
                bot_token TEXT,
                chat_id TEXT,
                strategy TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        print("🔧 Creando tabla auto_bots...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auto_bots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                status TEXT DEFAULT 'paused',
                exchange TEXT,
                api_key TEXT,
                api_secret TEXT,
                strategy TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        print("📊 Creando índices...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_subscriptions_user_status ON subscriptions(user_id, status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_subscriptions_end_date ON subscriptions(end_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_user ON payments(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_backtest_user_date ON backtest_results(user_id, created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_strategies_user ON strategies(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_signal_bots_user ON signal_bots(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_auto_bots_user ON auto_bots(user_id)")
        
        conn.commit()
        
        print("\n✅ ¡Base de datos de suscripciones creada exitosamente!")
        print("\n📋 Tablas creadas:")
        print("   • subscriptions - Gestión de planes de usuario")
        print("   • payments - Historial de pagos")
        print("   • backtest_results - Registro de backtests")
        print("   • strategies - Estrategias guardadas")
        print("   • signal_bots - Bots de señales")
        print("   • auto_bots - Bots de trading automático")
        
        # Verificar tablas creadas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"\n📊 Total de tablas en la base de datos: {len(tables)}")
        
    except Exception as e:
        print(f"\n❌ Error al crear tablas: {e}")
        conn.rollback()
    finally:
        conn.close()
        print("\n🔒 Conexión cerrada")

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 INICIALIZANDO SISTEMA DE SUSCRIPCIONES - DRAGLAB")
    print("=" * 60)
    print()
    
    init_subscriptions_db()
    
    print("\n" + "=" * 60)
    print("💡 SIGUIENTE PASO:")
    print("   1. Integrar subscription_routes.py en app.py")
    print("   2. Configurar pasarela de pagos (PayPal, Stripe, etc.)")
    print("   3. Probar flujo de suscripción")
    print("=" * 60)

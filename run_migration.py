import sqlite3
import sys

print("\n" + "="*60)
print("EJECUTANDO MIGRACION DE BASE DE DATOS")
print("="*60 + "\n")

try:
    conn = sqlite3.connect('database/app.db')
    cursor = conn.cursor()
    
    print("1. Creando tabla signal_bots...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS signal_bots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            bot_token TEXT NOT NULL,
            chat_id TEXT NOT NULL,
            symbol TEXT NOT NULL,
            timeframe TEXT NOT NULL,
            check_interval INTEGER NOT NULL DEFAULT 60,
            strategy TEXT,
            status TEXT DEFAULT 'paused',
            signals_sent INTEGER DEFAULT 0,
            uptime INTEGER DEFAULT 0,
            last_signal REAL,
            last_signal_text TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    print("   OK - Tabla signal_bots creada")
    
    print("\n2. Creando tabla bot_signals...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bot_signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bot_id INTEGER NOT NULL,
            signal_type TEXT NOT NULL,
            signal_text TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (bot_id) REFERENCES signal_bots (id) ON DELETE CASCADE
        )
    ''')
    print("   OK - Tabla bot_signals creada")
    
    print("\n3. Creando indices...")
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_signal_bots_user ON signal_bots(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_signal_bots_status ON signal_bots(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_bot_signals_bot ON bot_signals(bot_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_bot_signals_created ON bot_signals(created_at)')
    print("   OK - Indices creados")
    
    conn.commit()
    
    print("\n4. Verificando tablas creadas...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('signal_bots', 'bot_signals')")
    tables = cursor.fetchall()
    for table in tables:
        print(f"   OK - {table[0]} existe")
    
    cursor.execute("SELECT COUNT(*) FROM signal_bots")
    bot_count = cursor.fetchone()[0]
    print(f"\n5. Bots en base de datos: {bot_count}")
    
    conn.close()
    
    print("\n" + "="*60)
    print("MIGRACION COMPLETADA EXITOSAMENTE")
    print("="*60 + "\n")
    
    sys.exit(0)
    
except Exception as e:
    print(f"\nERROR: {e}\n")
    sys.exit(1)

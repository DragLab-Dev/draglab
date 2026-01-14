"""
Database Schema Updates for Signal Bots
Ejecuta este script para crear las tablas necesarias para el sistema de bots
"""

import sqlite3

def update_database():
    """Crear tablas para el sistema de bots de señales"""
    
    conn = sqlite3.connect('database/app.db')
    cursor = conn.cursor()
    
    # Tabla de bots de señales
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
    
    # Tabla de señales enviadas
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
    
    # Índices para mejorar rendimiento
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_signal_bots_user ON signal_bots(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_signal_bots_status ON signal_bots(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_bot_signals_bot ON bot_signals(bot_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_bot_signals_created ON bot_signals(created_at)')
    
    conn.commit()
    conn.close()
    
    print("✅ Database tables created successfully!")
    print("   - signal_bots: Tabla de bots de trading")
    print("   - bot_signals: Tabla de señales enviadas")

if __name__ == '__main__':
    update_database()

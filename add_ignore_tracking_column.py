"""
Migration: Add ignore_position_tracking column to signal_bots table
Ejecuta este script para agregar la columna ignore_position_tracking a la tabla signal_bots
"""

import sqlite3

def migrate_database():
    """Agregar columna ignore_position_tracking a signal_bots"""
    
    conn = sqlite3.connect('database/tradingbot.db')
    cursor = conn.cursor()
    
    try:
        # Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(signal_bots)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'ignore_position_tracking' not in columns:
            print("➕ Agregando columna 'ignore_position_tracking' a signal_bots...")
            cursor.execute('''
                ALTER TABLE signal_bots 
                ADD COLUMN ignore_position_tracking INTEGER DEFAULT 0
            ''')
            conn.commit()
            print("✅ Columna 'ignore_position_tracking' agregada exitosamente")
            print("   - 0 = Modo Profesional (respeta tracking de posiciones)")
            print("   - 1 = Modo Prueba (ignora tracking, siempre envía)")
        else:
            print("ℹ️  Columna 'ignore_position_tracking' ya existe")
        
        # Mostrar esquema actualizado
        print("\n📋 Esquema actual de signal_bots:")
        cursor.execute("PRAGMA table_info(signal_bots)")
        for col in cursor.fetchall():
            print(f"   - {col[1]} ({col[2]})")
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == '__main__':
    print("🚀 Iniciando migración de base de datos...")
    migrate_database()
    print("\n✅ Migración completada")

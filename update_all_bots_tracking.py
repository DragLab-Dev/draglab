"""
Script para actualizar todos los bots existentes y activar ignore_position_tracking
Ejecutar una sola vez: python update_all_bots_tracking.py
"""

import sqlite3
from datetime import datetime

def update_all_bots():
    print("🔧 Actualizando todos los bots para enviar señales continuas...")
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect('database/tradingbot.db')
        cursor = conn.cursor()
        
        # Actualizar todos los bots para que tengan ignore_position_tracking = 1 (True)
        cursor.execute('''
            UPDATE signal_bots 
            SET ignore_position_tracking = 1
        ''')
        
        affected_rows = cursor.rowcount
        conn.commit()
        
        print(f"✅ {affected_rows} bot(s) actualizado(s)")
        print("📡 Ahora todos los bots enviarán señales cada vez que la condición sea True")
        
        # Mostrar bots actualizados
        cursor.execute('SELECT id, name, ignore_position_tracking FROM signal_bots')
        bots = cursor.fetchall()
        
        print("\n📊 Estado de los bots:")
        for bot_id, name, tracking in bots:
            status = "✅ Señales continuas" if tracking == 1 else "❌ Solo cambios de estado"
            print(f"  • {name} (ID: {bot_id}) - {status}")
        
        conn.close()
        
        print("\n🎯 Para que los cambios tomen efecto:")
        print("   1. Si tienes bots activos, ve a la interfaz web")
        print("   2. Pausa cada bot")
        print("   3. Vuelve a activarlo")
        print("   4. O simplemente reinicia el servidor: python app.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    update_all_bots()

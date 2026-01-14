"""
Script para crear usuario administrador
Ejecutar: python create_admin.py
"""

import sqlite3
import os
from pathlib import Path
from werkzeug.security import generate_password_hash

# Configuración del admin
ADMIN_EMAIL = "admin@tradingbot.com"
ADMIN_PASSWORD = "Admin2026!"
ADMIN_NAME = "Administrador"

# Ruta de la base de datos
DB_PATH = Path(__file__).parent / "database" / "draglab.db"

def create_admin():
    """Crear usuario administrador en la base de datos"""
    
    # Verificar que existe la base de datos
    if not DB_PATH.exists():
        print("❌ Error: Base de datos no encontrada")
        print(f"   Ruta esperada: {DB_PATH}")
        print("\n💡 Ejecuta primero la aplicación para crear la base de datos:")
        print("   python app.py")
        return False
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar si el admin ya existe
        cursor.execute("SELECT id, email, role FROM users WHERE email=?", (ADMIN_EMAIL,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            user_id, email, role = existing_user
            if role == 'admin':
                print(f"✅ El usuario admin ya existe:")
                print(f"   📧 Email: {email}")
                print(f"   🆔 ID: {user_id}")
                print(f"   👑 Rol: {role}")
                print(f"\n🔑 Password: {ADMIN_PASSWORD}")
            else:
                # Actualizar rol a admin
                cursor.execute("UPDATE users SET role='admin' WHERE id=?", (user_id,))
                conn.commit()
                print(f"✅ Usuario actualizado a ADMIN:")
                print(f"   📧 Email: {email}")
                print(f"   🆔 ID: {user_id}")
                print(f"   👑 Rol: admin")
            conn.close()
            return True
        
        # Crear nuevo usuario admin
        hashed_password = generate_password_hash(ADMIN_PASSWORD)
        
        cursor.execute("""
            INSERT INTO users (email, password_hash, name, role, is_verified, created_at)
            VALUES (?, ?, ?, 'admin', 1, datetime('now'))
        """, (ADMIN_EMAIL, hashed_password, ADMIN_NAME))
        
        conn.commit()
        user_id = cursor.lastrowid
        
        print("=" * 60)
        print("✅ USUARIO ADMINISTRADOR CREADO EXITOSAMENTE")
        print("=" * 60)
        print(f"\n📧 Email:    {ADMIN_EMAIL}")
        print(f"🔑 Password: {ADMIN_PASSWORD}")
        print(f"🆔 ID:       {user_id}")
        print(f"👑 Rol:      admin")
        print(f"✅ Verificado: Sí")
        print("\n" + "=" * 60)
        print("ACCESO AL PANEL DE ADMINISTRACIÓN")
        print("=" * 60)
        print("\n🌐 URL Login: http://localhost:5000/login")
        print("🌐 URL Admin: http://localhost:5000/admin")
        print("\n⚠️  IMPORTANTE: Cambia la contraseña después del primer login")
        print("=" * 60)
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error al crear administrador: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("CREADOR DE USUARIO ADMINISTRADOR")
    print("Visual Strategy Creator")
    print("=" * 60 + "\n")
    
    create_admin()
    
    print("\n✨ Proceso completado\n")

"""
Script para actualizar el rol de un usuario a 'admin'
"""
import database as db

def update_user_to_admin(email):
    """Actualizar usuario a rol admin"""
    conn = db.get_db_connection()
    cursor = conn.cursor()
    
    # Verificar si el usuario existe
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    
    if not user:
        print(f"❌ Usuario {email} no encontrado")
        conn.close()
        return False
    
    # Mostrar información actual
    print(f"📋 Usuario encontrado:")
    print(f"   ID: {user['id']}")
    print(f"   Nombre: {user['name']}")
    print(f"   Email: {user['email']}")
    print(f"   Rol actual: {user['role']}")
    
    # Actualizar rol a admin
    cursor.execute('UPDATE users SET role = ? WHERE email = ?', ('admin', email))
    conn.commit()
    
    # Verificar actualización
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    updated_user = cursor.fetchone()
    
    print(f"\n✅ Usuario actualizado:")
    print(f"   Rol nuevo: {updated_user['role']}")
    
    conn.close()
    return True

if __name__ == '__main__':
    # Actualizar el usuario admin@vec a rol admin
    email = 'admin@vec'
    print(f"🔧 Actualizando usuario {email} a rol 'admin'...\n")
    update_user_to_admin(email)

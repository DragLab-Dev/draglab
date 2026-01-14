import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect('database/draglab.db')
cursor = conn.cursor()

# Actualizar contraseña
hashed = generate_password_hash('Admin2026!')
cursor.execute('''
    UPDATE users 
    SET password_hash=?, is_verified=1, role='admin' 
    WHERE email='admin@tradingbot.com'
''', (hashed,))
conn.commit()

print('✅ Contraseña actualizada para admin@tradingbot.com')

# Verificar
cursor.execute('SELECT id, email, role, is_verified FROM users WHERE email=?', ('admin@tradingbot.com',))
user = cursor.fetchone()
print(f'\n📋 Usuario actualizado:')
print(f'   ID: {user[0]}')
print(f'   Email: {user[1]}')
print(f'   Rol: {user[2]}')
print(f'   Verificado: {"Sí" if user[3] else "No"}')
print(f'\n🔑 Credenciales:')
print(f'   Email: admin@tradingbot.com')
print(f'   Password: Admin2026!')

conn.close()

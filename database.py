"""
Sistema de Base de Datos para TradingBot
Maneja usuarios, verificaciones, suscripciones y sesiones
"""

from datetime import datetime, timedelta
import sqlite3
import hashlib
import secrets
import json
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash

# Directorio de base de datos
DB_DIR = Path(__file__).parent / "database"
DB_DIR.mkdir(exist_ok=True)
DB_FILE = DB_DIR / "draglab.db"

def get_db_connection():
    """Crear conexión a la base de datos"""
    conn = sqlite3.connect(str(DB_FILE))
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Inicializar todas las tablas de la base de datos"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            name TEXT,
            google_id TEXT UNIQUE,
            is_verified INTEGER DEFAULT 0,
            role TEXT DEFAULT 'user',
            subscription_tier TEXT DEFAULT 'free',
            subscription_expires TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # Tabla de verificaciones de email
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS email_verifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            code TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            used INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Tabla de bots activos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_bots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            bot_type TEXT NOT NULL,
            symbol TEXT NOT NULL,
            timeframe TEXT NOT NULL,
            config TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_signal TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Tabla de backtests guardados
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_backtests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            symbol TEXT NOT NULL,
            timeframe TEXT NOT NULL,
            config TEXT NOT NULL,
            results TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Tabla de sesiones
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_token TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Tabla de planes de suscripción
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscription_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            display_name TEXT NOT NULL,
            price REAL NOT NULL,
            currency TEXT DEFAULT 'USD',
            duration_days INTEGER NOT NULL,
            max_backtests INTEGER,
            max_bots INTEGER,
            max_operations INTEGER,
            features TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla de suscripciones de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            plan_id INTEGER NOT NULL,
            status TEXT DEFAULT 'active',
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            payment_id TEXT,
            payment_method TEXT,
            auto_renew INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (plan_id) REFERENCES subscription_plans(id)
        )
    ''')
    
    # Tabla de uso de recursos (para controlar límites)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usage_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            resource_type TEXT NOT NULL,
            count INTEGER DEFAULT 1,
            date DATE DEFAULT CURRENT_DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Tabla de pagos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            subscription_id INTEGER,
            amount REAL NOT NULL,
            currency TEXT DEFAULT 'USD',
            payment_method TEXT NOT NULL,
            payment_id TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (subscription_id) REFERENCES user_subscriptions(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("[OK] Base de datos inicializada correctamente")

def hash_password(password):
    """Hash de contraseña con werkzeug (scrypt)"""
    return generate_password_hash(password)

def generate_verification_code():
    """Generar código de verificación de 4 dígitos"""
    return ''.join([str(secrets.randbelow(10)) for _ in range(4)])

def generate_session_token():
    """Generar token de sesión único"""
    return secrets.token_urlsafe(32)

# Funciones de Usuario
def create_user(email, password=None, name=None, google_id=None, role='user'):
    """Crear nuevo usuario"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        password_hash = hash_password(password) if password else None
        print(f"[DEBUG] Creando usuario: {email}, Role: {role}")
        if password_hash:
            print(f"[DEBUG] Hash generado: {password_hash[:50]}...")
        
        cursor.execute('''
            INSERT INTO users (email, password_hash, name, google_id, is_verified, role)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (email, password_hash, name, google_id, 1 if google_id else 0, role))
        
        user_id = cursor.lastrowid
        conn.commit()
        print(f"[DEBUG] ✓ Usuario creado con ID: {user_id}")
        
        # Si no es login con Google, crear código de verificación
        if not google_id:
            create_verification_code(user_id)
        
        return user_id
    except sqlite3.IntegrityError as e:
        print(f"[ERROR] Usuario ya existe: {e}")
        return None
    finally:
        conn.close()

def get_user_by_email(email):
    """Obtener usuario por email"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_id(user_id):
    """Obtener usuario por ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def verify_password(email, password):
    """Verificar contraseña del usuario - Retorna usuario solo si password es correcta"""
    user = get_user_by_email(email)
    if not user:
        print(f"[DEBUG] Usuario {email} no existe")
        return None
    
    if not user['password_hash']:
        print(f"[DEBUG] Usuario {email} no tiene password_hash")
        return None
    
    print(f"[DEBUG] Verificando password para {email}")
    print(f"[DEBUG] Hash en DB: {user['password_hash'][:50]}...")
    
    is_valid = check_password_hash(user['password_hash'], password)
    print(f"[DEBUG] Password válido: {is_valid}")
    
    if is_valid:
        return user
    return None

def update_password(user_id, new_password):
    """Actualizar contraseña del usuario"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        password_hash = hash_password(new_password)
        cursor.execute('''
            UPDATE users 
            SET password_hash = ?
            WHERE id = ?
        ''', (password_hash, user_id))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Error al actualizar contraseña: {e}")
        return False
    finally:
        conn.close()

# Alias para compatibilidad con admin panel
update_user_password = update_password

def delete_user(user_id):
    """Eliminar usuario y todos sus datos"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Eliminar todas las sesiones del usuario
        cursor.execute('DELETE FROM sessions WHERE user_id = ?', (user_id,))
        
        # Eliminar verificaciones de email
        cursor.execute('DELETE FROM email_verifications WHERE user_id = ?', (user_id,))
        
        # Eliminar bots del usuario
        cursor.execute('DELETE FROM user_bots WHERE user_id = ?', (user_id,))
        
        # Eliminar backtests del usuario
        cursor.execute('DELETE FROM user_backtests WHERE user_id = ?', (user_id,))
        
        # Eliminar el usuario
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Error al eliminar usuario: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

# Funciones de Verificación
def create_verification_code(user_id):
    """Crear código de verificación para usuario"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    code = generate_verification_code()
    expires_at = datetime.now() + timedelta(minutes=15)
    
    cursor.execute('''
        INSERT INTO email_verifications (user_id, code, expires_at)
        VALUES (?, ?, ?)
    ''', (user_id, code, expires_at))
    
    conn.commit()
    conn.close()
    return code

def verify_code(user_id, code):
    """Verificar código de email"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM email_verifications 
        WHERE user_id = ? AND code = ? AND used = 0 AND expires_at > ?
        ORDER BY created_at DESC LIMIT 1
    ''', (user_id, code, datetime.now()))
    
    verification = cursor.fetchone()
    
    if verification:
        # Marcar como usado
        cursor.execute('UPDATE email_verifications SET used = 1 WHERE id = ?', 
                      (verification['id'],))
        # Marcar usuario como verificado
        cursor.execute('UPDATE users SET is_verified = 1 WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
        return True
    
    conn.close()
    return False

# Funciones de Sesión
def create_session(user_id):
    """Crear sesión para usuario"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    token = generate_session_token()
    expires_at = datetime.now() + timedelta(days=30)
    
    cursor.execute('''
        INSERT INTO sessions (user_id, session_token, expires_at)
        VALUES (?, ?, ?)
    ''', (user_id, token, expires_at))
    
    # Actualizar último login
    cursor.execute('UPDATE users SET last_login = ? WHERE id = ?',
                  (datetime.now(), user_id))
    
    conn.commit()
    conn.close()
    return token

def get_session(token):
    """Obtener sesión por token"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            s.session_token, s.user_id, s.created_at, s.expires_at,
            u.id, u.email, u.name, u.role, u.is_verified, 
            u.subscription_tier, u.subscription_expires
        FROM sessions s
        JOIN users u ON s.user_id = u.id
        WHERE s.session_token = ? AND s.expires_at > datetime('now')
    ''', (token,))
    
    session = cursor.fetchone()
    conn.close()
    return dict(session) if session else None

def delete_session(token):
    """Eliminar sesión (logout)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM sessions WHERE session_token = ?', (token,))
    conn.commit()
    conn.close()

def get_user_by_session(token):
    """Obtener usuario por token de sesión (alias de get_session)"""
    session_data = get_session(token)
    if session_data:
        # Retornar solo los datos del usuario
        return {
            'id': session_data['id'],
            'email': session_data['email'],
            'name': session_data['name'],
            'role': session_data['role'],
            'is_verified': session_data['is_verified'],
            'subscription_tier': session_data['subscription_tier'],
            'subscription_expires': session_data.get('subscription_expires')
        }
    return None

# Funciones de Bots
def save_bot(user_id, bot_type, symbol, timeframe, config):
    """Guardar bot de usuario"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO user_bots (user_id, bot_type, symbol, timeframe, config)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, bot_type, symbol, timeframe, json.dumps(config)))
    
    bot_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return bot_id

def get_user_bots(user_id):
    """Obtener todos los bots del usuario"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM user_bots 
        WHERE user_id = ? AND status = 'active'
        ORDER BY created_at DESC
    ''', (user_id,))
    bots = cursor.fetchall()
    conn.close()
    return [dict(bot) for bot in bots]

def delete_bot(bot_id, user_id):
    """Eliminar bot (marcar como inactivo)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE user_bots SET status = 'inactive'
        WHERE id = ? AND user_id = ?
    ''', (bot_id, user_id))
    conn.commit()
    conn.close()

# Funciones de Backtests
def save_backtest(user_id, name, symbol, timeframe, config, results):
    """Guardar backtest del usuario"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO user_backtests (user_id, name, symbol, timeframe, config, results)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, name, symbol, timeframe, json.dumps(config), json.dumps(results)))
    
    backtest_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return backtest_id

def get_user_backtests(user_id, limit=10):
    """Obtener backtests del usuario"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM user_backtests 
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    ''', (user_id, limit))
    backtests = cursor.fetchall()
    conn.close()
    return [dict(bt) for bt in backtests]

# ==================== FUNCIONES DE SUSCRIPCIONES ====================

def init_subscription_plans():
    """Inicializar planes de suscripción predeterminados"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Verificar si ya existen planes
    cursor.execute('SELECT COUNT(*) as count FROM subscription_plans')
    if cursor.fetchone()['count'] > 0:
        conn.close()
        return
    
    plans = [
        {
            'name': 'free_trial',
            'display_name': 'Free Trial',
            'price': 0.0,
            'currency': 'USD',
            'duration_days': 7,
            'max_backtests': 5,
            'max_bots': 1,
            'max_operations': 20,
            'features': json.dumps([
                'Acceso a backtesting básico',
                'Hasta 5 backtests',
                '1 bot de señales activo',
                'Hasta 20 operaciones de prueba',
                'Soporte por email'
            ])
        },
        {
            'name': 'monthly',
            'display_name': 'Plan Mensual',
            'price': 29.99,
            'currency': 'USD',
            'duration_days': 30,
            'max_backtests': -1,  # -1 = ilimitado
            'max_bots': 5,
            'max_operations': -1,
            'features': json.dumps([
                'Backtesting ilimitado',
                'Hasta 5 bots simultáneos',
                'Operaciones ilimitadas',
                'Trading automático 24/7',
                'Indicadores avanzados',
                'Alertas en tiempo real',
                'Soporte prioritario'
            ])
        },
        {
            'name': 'annual',
            'display_name': 'Plan Anual',
            'price': 299.99,
            'currency': 'USD',
            'duration_days': 365,
            'max_backtests': -1,
            'max_bots': -1,  # ilimitado
            'max_operations': -1,
            'features': json.dumps([
                'TODO lo del Plan Mensual',
                'Bots ilimitados',
                'API avanzada',
                'Análisis personalizado',
                'Estrategias prediseñadas',
                'Acceso a comunidad premium',
                'Soporte 24/7',
                '2 meses GRATIS (ahorra $60)'
            ])
        }
    ]
    
    for plan in plans:
        cursor.execute('''
            INSERT INTO subscription_plans 
            (name, display_name, price, currency, duration_days, max_backtests, max_bots, max_operations, features)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            plan['name'], plan['display_name'], plan['price'], plan['currency'],
            plan['duration_days'], plan['max_backtests'], plan['max_bots'],
            plan['max_operations'], plan['features']
        ))
    
    conn.commit()
    conn.close()

def get_all_plans():
    """Obtener todos los planes de suscripción activos"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM subscription_plans 
        WHERE is_active = 1 
        ORDER BY price ASC
    ''')
    plans = cursor.fetchall()
    conn.close()
    return [dict(plan) for plan in plans]

def get_plan_by_name(plan_name):
    """Obtener plan por nombre"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM subscription_plans WHERE name = ?', (plan_name,))
    plan = cursor.fetchone()
    conn.close()
    return dict(plan) if plan else None

def create_subscription(user_id, plan_id, payment_id=None, payment_method=None):
    """Crear nueva suscripción para usuario"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Obtener información del plan
    cursor.execute('SELECT * FROM subscription_plans WHERE id = ?', (plan_id,))
    plan = cursor.fetchone()
    
    if not plan:
        conn.close()
        return None
    
    # Calcular fecha de expiración
    expires_at = datetime.now() + timedelta(days=plan['duration_days'])
    
    # Desactivar suscripciones anteriores
    cursor.execute('''
        UPDATE user_subscriptions 
        SET status = 'expired' 
        WHERE user_id = ? AND status = 'active'
    ''', (user_id,))
    
    # Crear nueva suscripción
    cursor.execute('''
        INSERT INTO user_subscriptions 
        (user_id, plan_id, expires_at, payment_id, payment_method)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, plan_id, expires_at, payment_id, payment_method))
    
    subscription_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return subscription_id

def get_user_subscription(user_id):
    """Obtener suscripción activa del usuario"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT us.*, sp.name as plan_name, sp.display_name, sp.max_backtests, 
               sp.max_bots, sp.max_operations, sp.features
        FROM user_subscriptions us
        JOIN subscription_plans sp ON us.plan_id = sp.id
        WHERE us.user_id = ? AND us.status = 'active' AND us.expires_at > datetime('now')
        ORDER BY us.expires_at DESC
        LIMIT 1
    ''', (user_id,))
    
    subscription = cursor.fetchone()
    conn.close()
    
    if subscription:
        return dict(subscription)
    
    # Si no tiene suscripción activa, devolver plan free trial
    return None

def track_usage(user_id, resource_type):
    """Registrar uso de recurso"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    today = datetime.now().date()
    
    # Verificar si ya existe un registro para hoy
    cursor.execute('''
        SELECT id, count FROM usage_tracking 
        WHERE user_id = ? AND resource_type = ? AND date = ?
    ''', (user_id, resource_type, today))
    
    existing = cursor.fetchone()
    
    if existing:
        # Actualizar contador
        cursor.execute('''
            UPDATE usage_tracking 
            SET count = count + 1 
            WHERE id = ?
        ''', (existing['id'],))
    else:
        # Crear nuevo registro
        cursor.execute('''
            INSERT INTO usage_tracking (user_id, resource_type, date, count)
            VALUES (?, ?, ?, 1)
        ''', (user_id, resource_type, today))
    
    conn.commit()
    conn.close()

def get_usage_count(user_id, resource_type, days=30):
    """Obtener conteo de uso en los últimos N días"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    date_from = (datetime.now() - timedelta(days=days)).date()
    
    cursor.execute('''
        SELECT COALESCE(SUM(count), 0) as total
        FROM usage_tracking 
        WHERE user_id = ? AND resource_type = ? AND date >= ?
    ''', (user_id, resource_type, date_from))
    
    result = cursor.fetchone()
    conn.close()
    
    return result['total'] if result else 0

def check_resource_limit(user_id, resource_type):
    """Verificar si el usuario puede usar un recurso"""
    subscription = get_user_subscription(user_id)
    
    # Si no tiene suscripción, asignar free trial automáticamente
    if not subscription:
        # Buscar plan free trial
        plan = get_plan_by_name('free_trial')
        if plan:
            create_subscription(user_id, plan['id'])
            subscription = get_user_subscription(user_id)
        else:
            return {'allowed': False, 'reason': 'No subscription found'}
    
    # Mapear tipo de recurso a límite
    limit_map = {
        'backtest': 'max_backtests',
        'bot': 'max_bots',
        'operation': 'max_operations'
    }
    
    limit_field = limit_map.get(resource_type)
    if not limit_field:
        return {'allowed': False, 'reason': 'Invalid resource type'}
    
    max_limit = subscription.get(limit_field, 0)
    
    # -1 significa ilimitado
    if max_limit == -1:
        return {'allowed': True, 'remaining': -1}
    
    # Obtener uso actual
    current_usage = get_usage_count(user_id, resource_type, days=30)
    
    if current_usage >= max_limit:
        return {
            'allowed': False,
            'reason': f'Límite alcanzado ({current_usage}/{max_limit})',
            'current': current_usage,
            'limit': max_limit
        }
    
    return {
        'allowed': True,
        'remaining': max_limit - current_usage,
        'current': current_usage,
        'limit': max_limit
    }

def create_payment(user_id, subscription_id, amount, currency, payment_method, payment_id):
    """Registrar pago"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO payments 
        (user_id, subscription_id, amount, currency, payment_method, payment_id, status)
        VALUES (?, ?, ?, ?, ?, ?, 'pending')
    ''', (user_id, subscription_id, amount, currency, payment_method, payment_id))
    
    payment_db_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return payment_db_id

def complete_payment(payment_db_id):
    """Marcar pago como completado"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE payments 
        SET status = 'completed', completed_at = datetime('now')
        WHERE id = ?
    ''', (payment_db_id,))
    
    conn.commit()
    conn.close()

# ==================== FUNCIONES DE ADMINISTRACIÓN ====================

def get_all_users():
    """Obtener todos los usuarios del sistema"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
    users = cursor.fetchall()
    conn.close()
    return [dict(user) for user in users]

def update_user_subscription(user_id, tier, expires_at):
    """Actualizar suscripción de un usuario"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE users 
            SET subscription_tier = ?, subscription_expires = ?
            WHERE id = ?
        ''', (tier, expires_at, user_id))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Error al actualizar suscripción: {e}")
        return False
    finally:
        conn.close()

def update_user_role(user_id, role):
    """Actualizar rol de un usuario"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE users 
            SET role = ?
            WHERE id = ?
        ''', (role, user_id))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Error al actualizar rol: {e}")
        return False
    finally:
        conn.close()

def update_user_verification(user_id, is_verified):
    """Actualizar estado de verificación de un usuario"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE users 
            SET is_verified = ?
            WHERE id = ?
        ''', (1 if is_verified else 0, user_id))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Error al actualizar verificación: {e}")
        return False
    finally:
        conn.close()

def get_all_bots():
    """Obtener todos los bots del sistema"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            b.*,
            u.email as user_email,
            u.name as user_name
        FROM user_bots b
        LEFT JOIN users u ON b.user_id = u.id
        ORDER BY b.created_at DESC
    ''')
    
    bots = cursor.fetchall()
    conn.close()
    return [dict(bot) for bot in bots]

def get_user_bots(user_id):
    """Obtener todos los bots de un usuario"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user_bots WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
    bots = cursor.fetchall()
    conn.close()
    return [dict(bot) for bot in bots]

def get_all_backtests():
    """Obtener todos los backtests del sistema"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            bt.*,
            u.email as user_email,
            u.name as user_name
        FROM user_backtests bt
        LEFT JOIN users u ON bt.user_id = u.id
        ORDER BY bt.created_at DESC
    ''')
    
    backtests = cursor.fetchall()
    conn.close()
    return [dict(bt) for bt in backtests]

def get_user_backtests(user_id):
    """Obtener todos los backtests de un usuario"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user_backtests WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
    backtests = cursor.fetchall()
    conn.close()
    return [dict(bt) for bt in backtests]

def delete_bot(bot_id):
    """Eliminar un bot"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM user_bots WHERE id = ?', (bot_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Error al eliminar bot: {e}")
        return False
    finally:
        conn.close()

def update_bot_status(bot_id, status):
    """Actualizar estado de un bot"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE user_bots 
            SET status = ?
            WHERE id = ?
        ''', (status, bot_id))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Error al actualizar estado del bot: {e}")
        return False
    finally:
        conn.close()

# Inicializar base de datos automáticamente cuando se importa
init_database()
init_subscription_plans()

# Crear usuario admin automáticamente si no existe
try:
    admin = get_user_by_email('admin@vec')
    if not admin:
        print("[INFO] Creando usuario admin por defecto...")
        admin_id = create_user('admin@vec', password='admin123', name='Administrador', role='admin')
        if admin_id:
            # Marcar como verificado
            conn = get_db_connection()
            conn.execute('UPDATE users SET is_verified = 1 WHERE id = ?', (admin_id,))
            conn.commit()
            conn.close()
            print("[INFO] ✓ Admin creado: admin@vec / admin123")
except Exception as e:
    print(f"[WARN] No se pudo crear admin automáticamente: {e}")

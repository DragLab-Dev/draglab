"""
Rutas de Autenticación para Flask
Maneja registro, login, verificación y gestión de usuarios
"""

from flask import Blueprint, request, jsonify, render_template, session, make_response, redirect, url_for
import os

# Importar database local
import database as db

auth_bp = Blueprint('auth', __name__)

# ==================== RUTAS DE PÁGINAS ====================

@auth_bp.route('/welcome')
def welcome_page():
    """Página de bienvenida (landing page)"""
    return render_template('welcome.html')

@auth_bp.route('/login')
def login_page():
    """Página de login"""
    google_client_id = os.getenv('GOOGLE_CLIENT_ID', '')
    return render_template('login.html', google_client_id=google_client_id)

@auth_bp.route('/register')
def register_page():
    """Página de registro"""
    google_client_id = os.getenv('GOOGLE_CLIENT_ID', '')
    return render_template('register.html', google_client_id=google_client_id)

# ==================== API DE AUTENTICACIÓN ====================

@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    """Registrar nuevo usuario"""
    try:
        data = request.json
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')

        # Validaciones
        if not email or not password:
            return jsonify({'error': 'Email y contraseña son requeridos'}), 400

        if len(password) < 8:
            return jsonify({'error': 'La contraseña debe tener al menos 8 caracteres'}), 400

        # Verificar si el usuario ya existe
        existing_user = db.get_user_by_email(email)
        
        if existing_user:
            # Si existe pero no está verificado, reenviar código
            if not existing_user['is_verified']:
                code = db.create_verification_code(existing_user['id'])
                try:
                    from email_service import send_verification_email
                    send_verification_email(email, code, existing_user['name'] or name)
                except Exception as email_error:
                    print(f"⚠️  No se pudo enviar email: {email_error}")
                
                return jsonify({
                    'success': True,
                    'message': 'Este email ya está registrado pero sin verificar. Te hemos enviado un nuevo código.',
                    'user_id': existing_user['id'],
                    'needs_verification': True
                })
            else:
                # Si ya está verificado, error
                return jsonify({'error': 'El email ya está registrado y verificado'}), 400
        
        # Crear nuevo usuario
        user_id = db.create_user(email=email, password=password, name=name)

        if not user_id:
            return jsonify({'error': 'Error al crear usuario'}), 400

        # Enviar código de verificación
        code = db.create_verification_code(user_id)
        
        try:
            from email_service import send_verification_email
            send_verification_email(email, code, name)
        except Exception as email_error:
            print(f"⚠️  No se pudo enviar email: {email_error}")

        return jsonify({
            'success': True,
            'message': 'Usuario creado exitosamente. Revisa tu email.',
            'user_id': user_id
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/api/auth/verify', methods=['POST'])
def verify_email():
    """Verificar código de email"""
    try:
        data = request.json
        user_id = data.get('user_id')
        code = data.get('code')

        if not user_id or not code:
            return jsonify({'error': 'User ID y código son requeridos'}), 400

        # Verificar código
        if db.verify_code(user_id, code):
            # Crear sesión
            token = db.create_session(user_id)
            user = db.get_user_by_id(user_id)
            
            # Guardar token en sesión de Flask
            session['session_token'] = token
            session['user_id'] = user['id']
            session.permanent = True

            # Enviar email de bienvenida
            try:
                from email_service import send_welcome_email
                send_welcome_email(user['email'], user['name'])
            except Exception as email_error:
                print(f"⚠️  No se pudo enviar email de bienvenida: {email_error}")

            return jsonify({
                'success': True,
                'message': 'Email verificado exitosamente',
                'token': token,
                'user': {
                    'id': user['id'],
                    'name': user['name'],
                    'email': user['email'],
                    'subscription_tier': user['subscription_tier']
                }
            })
        else:
            return jsonify({'error': 'Código incorrecto o expirado'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/api/auth/resend-code', methods=['POST'])
def resend_code():
    """Reenviar código de verificación"""
    try:
        data = request.json
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({'error': 'User ID es requerido'}), 400

        user = db.get_user_by_id(user_id)
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        # Crear nuevo código
        code = db.create_verification_code(user_id)
        
        try:
            from email_service import send_verification_email
            send_verification_email(user['email'], code, user['name'])
        except Exception as email_error:
            print(f"⚠️  No se pudo enviar email: {email_error}")

        return jsonify({
            'success': True,
            'message': 'Código reenviado exitosamente'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """Login con email y contraseña"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email y contraseña son requeridos'}), 400

        # Verificar credenciales
        user = db.verify_password(email, password)

        if not user:
            return jsonify({'error': 'Email o contraseña incorrectos'}), 401

        # Verificar que el usuario esté verificado
        if not user['is_verified']:
            return jsonify({'error': 'Debes verificar tu email primero'}), 403

        # Crear sesión
        token = db.create_session(user['id'])
        
        # Guardar token en sesión de Flask
        session['session_token'] = token
        session['user_id'] = user['id']
        session.permanent = True  # Hacer la sesión permanente (30 días)

        return jsonify({
            'success': True,
            'message': 'Login exitoso',
            'token': token,
            'user': {
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'subscription_tier': user['subscription_tier']
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/api/auth/google', methods=['POST'])
def google_login():
    """Login con Google OAuth"""
    try:
        data = request.json
        token = data.get('token')

        if not token:
            return jsonify({'error': 'Token de Google es requerido'}), 400

        # Verificar token de Google
        try:
            from google_auth import verify_google_token
            google_user = verify_google_token(token)
        except Exception as google_error:
            print(f"⚠️  Error con Google Auth: {google_error}")
            google_user = None

        if not google_user:
            return jsonify({'error': 'Token de Google inválido'}), 401

        # Buscar usuario existente
        user = db.get_user_by_email(google_user['email'])

        if not user:
            # Crear nuevo usuario con Google
            user_id = db.create_user(
                email=google_user['email'],
                name=google_user['name'],
                google_id=google_user['google_id']
            )
            user = db.get_user_by_id(user_id)

        # Crear sesión
        session_token = db.create_session(user['id'])
        
        # Guardar token en sesión de Flask
        session['session_token'] = session_token
        session['user_id'] = user['id']
        session.permanent = True

        return jsonify({
            'success': True,
            'message': 'Login con Google exitoso',
            'token': session_token,
            'user': {
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'subscription_tier': user['subscription_tier']
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    """Cerrar sesión"""
    try:
        # Obtener token de la sesión o del request
        token = session.get('session_token') or request.json.get('token') if request.json else None

        if token:
            db.delete_session(token)
        
        # Limpiar sesión de Flask
        session.pop('session_token', None)
        session.pop('user_id', None)

        return jsonify({
            'success': True,
            'message': 'Sesión cerrada exitosamente'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/api/auth/me', methods=['GET'])
def get_current_user():
    """Obtener información del usuario actual"""
    try:
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token no proporcionado'}), 401

        token = auth_header.split(' ')[1]
        session = db.get_session(token)

        if not session:
            return jsonify({'error': 'Sesión inválida o expirada'}), 401

        return jsonify({
            'success': True,
            'user': {
                'id': session['id'],
                'name': session['name'],
                'email': session['email'],
                'role': session.get('role', 'user'),
                'subscription_tier': session['subscription_tier'],
                'subscription_expires': session['subscription_expires'],
                'is_verified': session['is_verified']
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== API DE USUARIO ====================

@auth_bp.route('/api/user-info', methods=['GET'])
def get_user_info():
    """Obtener información detallada del usuario desde sesión Flask"""
    try:
        # Obtener user_id de la sesión de Flask
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'No hay sesión activa'}), 401

        user = db.get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'role': user.get('role', 'user'),
                'subscription_tier': user['subscription_tier'],
                'subscription_expires': user.get('subscription_expires'),
                'created_at': user.get('created_at'),
                'is_verified': user['is_verified']
            },
            'is_admin': user.get('role', 'user') == 'admin'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/api/change-password', methods=['POST'])
def change_password():
    """Cambiar contraseña del usuario"""
    try:
        # Obtener user_id de la sesión de Flask
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'No hay sesión activa'}), 401

        data = request.json
        current_password = data.get('currentPassword')
        new_password = data.get('newPassword')

        if not current_password or not new_password:
            return jsonify({'error': 'Contraseña actual y nueva son requeridas'}), 400

        if len(new_password) < 8:
            return jsonify({'error': 'La nueva contraseña debe tener al menos 8 caracteres'}), 400

        # Obtener usuario
        user = db.get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        # Verificar contraseña actual
        verified_user = db.verify_password(user['email'], current_password)
        
        if not verified_user:
            return jsonify({'error': 'Contraseña actual incorrecta'}), 401

        # Cambiar contraseña
        success = db.update_password(user_id, new_password)
        
        if not success:
            return jsonify({'error': 'Error al cambiar contraseña'}), 500

        return jsonify({
            'success': True,
            'message': 'Contraseña cambiada exitosamente'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/api/delete-account', methods=['DELETE'])
def delete_account():
    """Eliminar cuenta del usuario"""
    try:
        # Obtener user_id de la sesión de Flask
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'No hay sesión activa'}), 401

        data = request.json
        password = data.get('password')

        if not password:
            return jsonify({'error': 'Contraseña es requerida para eliminar cuenta'}), 400

        # Obtener usuario
        user = db.get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        # Verificar contraseña
        verified_user = db.verify_password(user['email'], password)
        
        if not verified_user:
            return jsonify({'error': 'Contraseña incorrecta'}), 401

        # Eliminar usuario y todas sus sesiones
        success = db.delete_user(user_id)
        
        if not success:
            return jsonify({'error': 'Error al eliminar cuenta'}), 500

        # Limpiar sesión de Flask
        session.pop('session_token', None)
        session.pop('user_id', None)

        return jsonify({
            'success': True,
            'message': 'Cuenta eliminada exitosamente'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

"""
Rutas de Administración
Maneja funcionalidades exclusivas para administradores
"""

from flask import Blueprint, request, jsonify, render_template, session
from functools import wraps
import database as db
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# ==================== MIDDLEWARE ====================

def admin_required(f):
    """Decorador para rutas que requieren rol de admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'No autenticado'}), 401
        
        user = db.get_user_by_id(user_id)
        
        if not user or user.get('role') != 'admin':
            return jsonify({'error': 'Acceso denegado. Requiere rol de administrador'}), 403
        
        return f(*args, **kwargs)
    return decorated_function


# ==================== PÁGINAS ====================

@admin_bp.route('/panel')
@admin_required
def admin_panel():
    """Página del panel de administración"""
    user_id = session.get('user_id')
    admin_user = db.get_user_by_id(user_id)
    return render_template('admin_panel.html', admin=admin_user)


# ==================== ESTADÍSTICAS ====================

@admin_bp.route('/api/stats', methods=['GET'])
@admin_required
def get_stats():
    """Obtener estadísticas generales del sistema"""
    try:
        # Estadísticas de usuarios
        all_users = db.get_all_users()
        total_users = len(all_users)
        verified_users = sum(1 for u in all_users if u['is_verified'])
        unverified_users = total_users - verified_users
        admin_users = sum(1 for u in all_users if u.get('role') == 'admin')
        
        # Usuarios registrados hoy, esta semana, este mes
        now = datetime.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        users_today = sum(1 for u in all_users 
                         if u.get('created_at') and datetime.fromisoformat(u['created_at']) >= today)
        users_week = sum(1 for u in all_users 
                        if u.get('created_at') and datetime.fromisoformat(u['created_at']) >= week_ago)
        users_month = sum(1 for u in all_users 
                         if u.get('created_at') and datetime.fromisoformat(u['created_at']) >= month_ago)
        
        # Estadísticas de suscripciones
        subscriptions_by_tier = {}
        for user in all_users:
            tier = user.get('subscription_tier', 'free')
            subscriptions_by_tier[tier] = subscriptions_by_tier.get(tier, 0) + 1
        
        # Estadísticas de bots
        all_bots = db.get_all_bots() if hasattr(db, 'get_all_bots') else []
        total_bots = len(all_bots)
        active_bots = sum(1 for b in all_bots if b.get('status') == 'active')
        
        # Estadísticas de backtests
        all_backtests = db.get_all_backtests() if hasattr(db, 'get_all_backtests') else []
        total_backtests = len(all_backtests)
        
        return jsonify({
            'success': True,
            'stats': {
                'users': {
                    'total': total_users,
                    'verified': verified_users,
                    'unverified': unverified_users,
                    'admins': admin_users,
                    'today': users_today,
                    'week': users_week,
                    'month': users_month
                },
                'subscriptions': subscriptions_by_tier,
                'bots': {
                    'total': total_bots,
                    'active': active_bots,
                    'inactive': total_bots - active_bots
                },
                'backtests': {
                    'total': total_backtests
                }
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== GESTIÓN DE USUARIOS ====================

@admin_bp.route('/api/users', methods=['GET'])
@admin_required
def get_all_users_admin():
    """Obtener lista de todos los usuarios"""
    try:
        users = db.get_all_users()
        
        # Formatear datos de usuarios
        users_data = []
        for user in users:
            users_data.append({
                'id': user['id'],
                'email': user['email'],
                'name': user.get('name', ''),
                'role': user.get('role', 'user'),
                'is_verified': user['is_verified'],
                'subscription_tier': user.get('subscription_tier', 'free'),
                'subscription_expires': user.get('subscription_expires'),
                'created_at': user.get('created_at'),
                'last_login': user.get('last_login')
            })
        
        return jsonify({
            'success': True,
            'users': users_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user_details(user_id):
    """Obtener detalles de un usuario específico"""
    try:
        user = db.get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Obtener bots del usuario
        user_bots = db.get_user_bots(user_id) if hasattr(db, 'get_user_bots') else []
        
        # Obtener backtests del usuario
        user_backtests = db.get_user_backtests(user_id) if hasattr(db, 'get_user_backtests') else []
        
        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'name': user.get('name', ''),
                'role': user.get('role', 'user'),
                'is_verified': user['is_verified'],
                'subscription_tier': user.get('subscription_tier', 'free'),
                'subscription_expires': user.get('subscription_expires'),
                'created_at': user.get('created_at'),
                'last_login': user.get('last_login'),
                'bots_count': len(user_bots),
                'backtests_count': len(user_backtests)
            },
            'bots': user_bots,
            'backtests': user_backtests
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/users/<int:user_id>/subscription', methods=['POST'])
@admin_required
def update_user_subscription(user_id):
    """Actualizar suscripción de un usuario"""
    try:
        data = request.json
        tier = data.get('tier')
        duration_days = data.get('duration_days', 30)
        
        if not tier:
            return jsonify({'error': 'Tier es requerido'}), 400
        
        # Calcular fecha de expiración
        expires_at = datetime.now() + timedelta(days=duration_days)
        
        # Actualizar suscripción
        success = db.update_user_subscription(user_id, tier, expires_at)
        
        if not success:
            return jsonify({'error': 'Error al actualizar suscripción'}), 500
        
        return jsonify({
            'success': True,
            'message': f'Suscripción actualizada a {tier}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/users/<int:user_id>/role', methods=['POST'])
@admin_required
def update_user_role(user_id):
    """Actualizar rol de un usuario"""
    try:
        data = request.json
        new_role = data.get('role')
        
        if not new_role or new_role not in ['user', 'admin']:
            return jsonify({'error': 'Rol inválido'}), 400
        
        # No permitir que admin se quite a sí mismo el rol
        current_user_id = session.get('user_id')
        if user_id == current_user_id and new_role != 'admin':
            return jsonify({'error': 'No puedes quitarte a ti mismo el rol de admin'}), 400
        
        success = db.update_user_role(user_id, new_role)
        
        if not success:
            return jsonify({'error': 'Error al actualizar rol'}), 500
        
        return jsonify({
            'success': True,
            'message': f'Rol actualizado a {new_role}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/users/<int:user_id>/verify', methods=['POST'])
@admin_required
def toggle_user_verification(user_id):
    """Verificar o desverificar usuario"""
    try:
        user = db.get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        new_status = not user['is_verified']
        success = db.update_user_verification(user_id, new_status)
        
        if not success:
            return jsonify({'error': 'Error al actualizar verificación'}), 500
        
        return jsonify({
            'success': True,
            'is_verified': new_status,
            'message': 'Usuario verificado' if new_status else 'Verificación removida'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user_admin(user_id):
    """Eliminar usuario desde panel de admin"""
    try:
        # No permitir que admin se elimine a sí mismo
        current_user_id = session.get('user_id')
        if user_id == current_user_id:
            return jsonify({'error': 'No puedes eliminarte a ti mismo'}), 400
        
        success = db.delete_user(user_id)
        
        if not success:
            return jsonify({'error': 'Error al eliminar usuario'}), 500
        
        return jsonify({
            'success': True,
            'message': 'Usuario eliminado exitosamente'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/users/create', methods=['POST'])
@admin_required
def create_user_admin():
    """Crear nuevo usuario desde panel de admin"""
    try:
        data = request.json
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        name = data.get('name', '').strip()
        role = data.get('role', 'user')
        is_verified = data.get('is_verified', False)
        
        # Validaciones
        if not email:
            return jsonify({'error': 'El email es obligatorio'}), 400
        
        if not password:
            return jsonify({'error': 'La contraseña es obligatoria'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'La contraseña debe tener al menos 6 caracteres'}), 400
        
        if role not in ['user', 'admin']:
            return jsonify({'error': 'Rol inválido'}), 400
        
        # Verificar si el email ya existe
        existing_user = db.get_user_by_email(email)
        if existing_user:
            return jsonify({'error': 'El email ya está registrado'}), 400
        
        # Crear usuario
        user = db.create_user(email=email, password=password, name=name, role=role)
        
        if not user:
            return jsonify({'error': 'Error al crear usuario'}), 500
        
        # Actualizar estado de verificación si es necesario
        if is_verified:
            db.update_user_verification(user['id'], True)
        
        return jsonify({
            'success': True,
            'message': f'Usuario {email} creado exitosamente',
            'user_id': user['id']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/users/<int:user_id>/reset-password', methods=['POST'])
@admin_required
def reset_user_password(user_id):
    """Resetear contraseña de usuario"""
    try:
        import random
        import string
        
        user = db.get_user_by_id(user_id)
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Generar contraseña temporal aleatoria
        new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        
        # Actualizar contraseña
        success = db.update_user_password(user_id, new_password)
        
        if not success:
            return jsonify({'error': 'Error al resetear contraseña'}), 500
        
        return jsonify({
            'success': True,
            'message': 'Contraseña reseteada exitosamente',
            'email': user['email'],
            'new_password': new_password
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/users/<int:user_id>/change-role', methods=['POST'])
@admin_required
def change_user_role(user_id):
    """Cambiar rol de usuario"""
    try:
        data = request.json
        new_role = data.get('role')
        
        if not new_role or new_role not in ['user', 'admin']:
            return jsonify({'error': 'Rol inválido'}), 400
        
        # No permitir que admin se quite a sí mismo el rol
        current_user_id = session.get('user_id')
        if user_id == current_user_id and new_role != 'admin':
            return jsonify({'error': 'No puedes quitarte a ti mismo el rol de admin'}), 400
        
        success = db.update_user_role(user_id, new_role)
        
        if not success:
            return jsonify({'error': 'Error al actualizar rol'}), 500
        
        return jsonify({
            'success': True,
            'message': f'Rol actualizado a {new_role}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/users/<int:user_id>/toggle-verification', methods=['POST'])
@admin_required
def toggle_verification(user_id):
    """Alternar verificación de usuario"""
    try:
        user = db.get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        new_status = not user['is_verified']
        success = db.update_user_verification(user_id, new_status)
        
        if not success:
            return jsonify({'error': 'Error al actualizar verificación'}), 500
        
        return jsonify({
            'success': True,
            'is_verified': new_status,
            'message': 'Usuario verificado' if new_status else 'Verificación removida'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/users/<int:user_id>/resend-verification', methods=['POST'])
@admin_required
def resend_verification(user_id):
    """Reenviar código de verificación"""
    try:
        user = db.get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        if user['is_verified']:
            return jsonify({'error': 'Usuario ya está verificado'}), 400
        
        # Crear nuevo código de verificación
        code = db.create_verification_code(user_id)
        
        if not code:
            return jsonify({'error': 'Error al generar código'}), 500
        
        # Aquí se podría enviar el email con el código
        # from email_service import send_verification_email
        # send_verification_email(user['email'], code)
        
        return jsonify({
            'success': True,
            'message': f'Código de verificación enviado a {user["email"]}',
            'code': code  # Solo para testing, remover en producción
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== GESTIÓN DE BOTS ====================

@admin_bp.route('/api/bots', methods=['GET'])
@admin_required
def get_all_bots():
    """Obtener todos los bots de todos los usuarios"""
    try:
        bots = db.get_all_bots() if hasattr(db, 'get_all_bots') else []
        
        return jsonify({
            'success': True,
            'bots': bots
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/bots/<int:bot_id>', methods=['DELETE'])
@admin_required
def delete_bot_admin(bot_id):
    """Eliminar bot desde panel de admin"""
    try:
        success = db.delete_bot(bot_id) if hasattr(db, 'delete_bot') else False
        
        if not success:
            return jsonify({'error': 'Error al eliminar bot'}), 500
        
        return jsonify({
            'success': True,
            'message': 'Bot eliminado exitosamente'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/bots/<int:bot_id>/status', methods=['POST'])
@admin_required
def update_bot_status(bot_id):
    """Actualizar estado de un bot"""
    try:
        data = request.json
        status = data.get('status')
        
        if status not in ['active', 'paused', 'stopped']:
            return jsonify({'error': 'Estado inválido'}), 400
        
        success = db.update_bot_status(bot_id, status) if hasattr(db, 'update_bot_status') else False
        
        if not success:
            return jsonify({'error': 'Error al actualizar estado'}), 500
        
        return jsonify({
            'success': True,
            'message': f'Bot {status}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== GESTIÓN DE SUSCRIPCIONES ====================

@admin_bp.route('/api/subscriptions/plans', methods=['GET'])
@admin_required
def get_subscription_plans():
    """Obtener todos los planes de suscripción"""
    try:
        plans = db.get_all_plans() if hasattr(db, 'get_all_plans') else []
        
        return jsonify({
            'success': True,
            'plans': plans
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/subscriptions/stats', methods=['GET'])
@admin_required
def get_subscription_stats():
    """Obtener estadísticas de suscripciones"""
    try:
        users = db.get_all_users()
        
        stats = {
            'free': 0,
            'basic': 0,
            'pro': 0,
            'premium': 0,
            'expired': 0,
            'revenue': 0  # Para implementar con pagos reales
        }
        
        for user in users:
            tier = user.get('subscription_tier', 'free')
            stats[tier] = stats.get(tier, 0) + 1
            
            # Verificar si está expirada
            if user.get('subscription_expires'):
                try:
                    expires_at = datetime.fromisoformat(user['subscription_expires'])
                    if expires_at < datetime.now():
                        stats['expired'] += 1
                except:
                    pass
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

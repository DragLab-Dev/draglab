"""
Sistema de Pagos Simulado (Demo)
Para testing y desarrollo - Simula pasarela de pagos real
En producción: Integrar con Stripe, PayPal, etc.
"""

from flask import Blueprint, request, jsonify, session
from functools import wraps
import database as db
from datetime import datetime, timedelta
import secrets
import json

payments_bp = Blueprint('payments', __name__, url_prefix='/api/payments')

# ==================== CONFIGURACIÓN ====================

# Planes y precios (en USD)
PRICING = {
    'basic': {
        'monthly': 9.99,
        'yearly': 99.99,
        'currency': 'USD'
    },
    'pro': {
        'monthly': 19.99,
        'yearly': 199.99,
        'currency': 'USD'
    },
    'premium': {
        'monthly': 49.99,
        'yearly': 499.99,
        'currency': 'USD'
    }
}

# Métodos de pago simulados
PAYMENT_METHODS = ['credit_card', 'paypal', 'stripe', 'crypto']

# ==================== MIDDLEWARE ====================

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'No autenticado'}), 401
        return f(user_id, *args, **kwargs)
    return decorated_function

# ==================== ENDPOINTS ====================

@payments_bp.route('/pricing', methods=['GET'])
def get_pricing():
    """Obtener precios de todos los planes"""
    return jsonify({
        'success': True,
        'pricing': PRICING,
        'note': 'Sistema de pagos en modo DEMO - No se procesan pagos reales'
    })


@payments_bp.route('/create-checkout', methods=['POST'])
@require_auth
def create_checkout(user_id):
    """
    Crear sesión de pago simulada
    En producción: Integrar con Stripe Checkout o similar
    """
    try:
        data = request.json
        plan = data.get('plan')  # basic, pro, premium
        billing_cycle = data.get('billing_cycle', 'monthly')  # monthly, yearly
        
        if plan not in PRICING:
            return jsonify({'error': 'Plan inválido'}), 400
        
        if billing_cycle not in ['monthly', 'yearly']:
            return jsonify({'error': 'Ciclo de facturación inválido'}), 400
        
        # Obtener precio
        amount = PRICING[plan][billing_cycle]
        currency = PRICING[plan]['currency']
        
        # Generar ID de sesión simulado
        checkout_id = f"checkout_{secrets.token_hex(16)}"
        
        # En DEMO: Auto-completar el pago después de 2 segundos
        # En producción: Redirigir a página de pago real
        
        return jsonify({
            'success': True,
            'checkout_id': checkout_id,
            'amount': amount,
            'currency': currency,
            'plan': plan,
            'billing_cycle': billing_cycle,
            'demo_mode': True,
            'message': 'DEMO: Pago se completará automáticamente'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@payments_bp.route('/complete-demo-payment', methods=['POST'])
@require_auth
def complete_demo_payment(user_id):
    """
    Completar pago en modo DEMO
    Simula webhook de pasarela de pagos
    """
    try:
        data = request.json
        checkout_id = data.get('checkout_id')
        plan = data.get('plan')
        billing_cycle = data.get('billing_cycle', 'monthly')
        payment_method = data.get('payment_method', 'demo_card')
        
        if not checkout_id or not plan:
            return jsonify({'error': 'Datos incompletos'}), 400
        
        # Calcular duración de suscripción
        duration_days = 365 if billing_cycle == 'yearly' else 30
        expires_at = datetime.now() + timedelta(days=duration_days)
        
        # Actualizar suscripción del usuario
        success = db.update_user_subscription(user_id, plan, expires_at)
        
        if not success:
            return jsonify({'error': 'Error al actualizar suscripción'}), 500
        
        # Registrar pago en historial (opcional)
        amount = PRICING[plan][billing_cycle]
        payment_id = f"pay_demo_{secrets.token_hex(12)}"
        
        # Crear registro de pago
        try:
            db.create_payment(
                user_id=user_id,
                subscription_id=0,  # No hay subscription_id en demo
                amount=amount,
                currency='USD',
                payment_method=payment_method,
                payment_id=payment_id
            )
        except Exception as e:
            print(f"⚠️ No se pudo registrar pago: {e}")
        
        return jsonify({
            'success': True,
            'message': f'Suscripción {plan} activada exitosamente',
            'subscription': {
                'tier': plan,
                'expires_at': expires_at.isoformat(),
                'billing_cycle': billing_cycle,
                'amount': amount,
                'currency': 'USD'
            },
            'demo_mode': True
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@payments_bp.route('/cancel-subscription', methods=['POST'])
@require_auth
def cancel_subscription(user_id):
    """
    Cancelar suscripción actual
    En producción: Cancelar en pasarela de pagos
    """
    try:
        # Obtener usuario
        user = db.get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        current_tier = user.get('subscription_tier', 'free')
        
        if current_tier == 'free':
            return jsonify({'error': 'No tienes suscripción activa'}), 400
        
        # Bajar a plan free al expirar
        # No cancelar inmediatamente - dejar que expire
        return jsonify({
            'success': True,
            'message': 'Suscripción cancelada. Se desactivará al finalizar el período actual',
            'expires_at': user.get('subscription_expires'),
            'note': 'En DEMO: Para cancelar inmediatamente, el admin puede cambiar tu plan'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@payments_bp.route('/payment-history', methods=['GET'])
@require_auth
def get_payment_history(user_id):
    """Obtener historial de pagos del usuario"""
    try:
        # Obtener pagos del usuario (si existe tabla de pagos)
        try:
            conn = db.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM payments 
                WHERE user_id = ? 
                ORDER BY created_at DESC
            ''', (user_id,))
            payments = cursor.fetchall()
            conn.close()
            
            payments_list = [dict(p) for p in payments]
        except Exception as e:
            print(f"⚠️ Tabla payments no existe: {e}")
            payments_list = []
        
        return jsonify({
            'success': True,
            'payments': payments_list
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@payments_bp.route('/verify-payment/<payment_id>', methods=['GET'])
@require_auth
def verify_payment(user_id, payment_id):
    """
    Verificar estado de un pago
    En producción: Consultar con la pasarela de pagos
    """
    try:
        # En DEMO: Simular verificación exitosa
        return jsonify({
            'success': True,
            'payment_id': payment_id,
            'status': 'completed',
            'demo_mode': True,
            'message': 'Pago verificado (DEMO)'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== WEBHOOKS (SIMULADOS) ====================

@payments_bp.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    """
    Webhook simulado de Stripe
    En producción: Verificar firma y procesar eventos reales
    """
    try:
        # En producción:
        # 1. Verificar firma del webhook
        # 2. Parsear evento
        # 3. Actualizar suscripción según evento
        
        data = request.json
        event_type = data.get('type', 'payment_intent.succeeded')
        
        print(f"📬 Webhook Stripe (DEMO): {event_type}")
        
        return jsonify({'received': True, 'demo': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@payments_bp.route('/webhook/paypal', methods=['POST'])
def paypal_webhook():
    """
    Webhook simulado de PayPal
    En producción: Verificar y procesar eventos de PayPal
    """
    try:
        data = request.json
        event_type = data.get('event_type', 'PAYMENT.CAPTURE.COMPLETED')
        
        print(f"📬 Webhook PayPal (DEMO): {event_type}")
        
        return jsonify({'received': True, 'demo': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== GUÍA DE INTEGRACIÓN ====================

@payments_bp.route('/integration-guide', methods=['GET'])
def get_integration_guide():
    """Obtener guía de integración con pasarelas reales"""
    guide = {
        'stripe': {
            'docs': 'https://stripe.com/docs/payments',
            'setup': [
                '1. Crear cuenta en Stripe',
                '2. Obtener API keys (publishable y secret)',
                '3. pip install stripe',
                '4. Configurar webhooks en dashboard',
                '5. Implementar Stripe Checkout',
                '6. Manejar eventos de webhook'
            ],
            'example': 'stripe.checkout.Session.create(...)'
        },
        'paypal': {
            'docs': 'https://developer.paypal.com/docs/api/overview/',
            'setup': [
                '1. Crear cuenta Business en PayPal',
                '2. Obtener credenciales de API',
                '3. pip install paypalrestsdk',
                '4. Configurar webhooks',
                '5. Implementar PayPal Checkout',
                '6. Verificar pagos'
            ],
            'example': 'paypalrestsdk.Payment.create(...)'
        },
        'current_status': 'DEMO MODE - Simulación de pagos para testing',
        'note': 'Actualizar payments_routes.py para integración real'
    }
    
    return jsonify({
        'success': True,
        'guide': guide
    })

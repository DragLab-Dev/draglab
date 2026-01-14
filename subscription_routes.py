"""
Sistema de Suscripciones - DragLab
Maneja planes, límites de uso y pagos
"""

from flask import Blueprint, request, jsonify, session
from database import get_db_connection
from datetime import datetime, timedelta
import json

subscription_bp = Blueprint('subscriptions', __name__, url_prefix='/api/subscriptions')

# Definición de planes predefinidos
PLANS = {
    'free_trial': {
        'name': 'free_trial',
        'display_name': '🆓 Free Trial',
        'price': 0,
        'currency': 'USD',
        'duration_days': 14,
        'limits': {
            'backtests': 10,
            'signal_bots': 1,
            'auto_bots': 0,
            'operations_per_day': 5,
            'indicators': 3,
            'strategies': 2
        },
        'features': [
            '✓ 10 Backtests incluidos',
            '✓ 1 Signal Bot activo',
            '✓ 3 Indicadores técnicos',
            '✓ 2 Estrategias guardadas',
            '✓ 5 Operaciones/día',
            '✓ Constructor visual básico',
            '✓ Señales por Telegram',
            '✓ Soporte por email',
            '⚠️ 14 días de prueba'
        ]
    },
    'pro_monthly': {
        'name': 'pro_monthly',
        'display_name': '💼 Pro Monthly',
        'price': 29.99,
        'currency': 'USD',
        'duration_days': 30,
        'limits': {
            'backtests': 100,
            'signal_bots': 5,
            'auto_bots': 2,
            'operations_per_day': 50,
            'indicators': -1,  # -1 = ilimitado
            'strategies': 10
        },
        'features': [
            '✓ 100 Backtests/mes',
            '✓ 5 Signal Bots simultáneos',
            '✓ 2 Auto Trading Bots',
            '✓ Indicadores ilimitados',
            '✓ 10 Estrategias guardadas',
            '✓ 50 Operaciones/día',
            '✓ Constructor visual avanzado',
            '✓ Gestión de riesgo automática',
            '✓ Stop-Loss y Take-Profit',
            '✓ Historial completo de señales',
            '✓ Análisis de rendimiento',
            '✓ Soporte prioritario 24/7',
            '✓ Actualizaciones automáticas'
        ]
    },
    'pro_annual': {
        'name': 'pro_annual',
        'display_name': '👑 Pro Annual',
        'price': 299.99,
        'currency': 'USD',
        'duration_days': 365,
        'discount': '17% OFF',
        'limits': {
            'backtests': -1,
            'signal_bots': -1,
            'auto_bots': -1,
            'operations_per_day': -1,
            'indicators': -1,
            'strategies': -1
        },
        'features': [
            '✓ Backtests ILIMITADOS',
            '✓ Signal Bots ILIMITADOS',
            '✓ Auto Trading Bots ILIMITADOS',
            '✓ Indicadores ILIMITADOS',
            '✓ Estrategias ILIMITADAS',
            '✓ Operaciones ILIMITADAS',
            '✓ Constructor visual premium',
            '✓ API REST avanzada',
            '✓ Webhooks personalizados',
            '✓ Gestión de múltiples exchanges',
            '✓ Backtesting con datos históricos premium',
            '✓ Machine Learning signals (próximamente)',
            '✓ Soporte VIP 24/7',
            '✓ Acceso anticipado a nuevas features',
            '✓ Ahorra $60/año vs mensual'
        ]
    }
}

@subscription_bp.route('/plans', methods=['GET'])
def get_plans():
    """Obtener todos los planes disponibles"""
    try:
        plans_list = []
        for plan_name, plan_data in PLANS.items():
            plans_list.append({
                **plan_data,
                'features': plan_data['features']  # Ya es lista
            })
        
        return jsonify({
            'success': True,
            'plans': plans_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@subscription_bp.route('/current', methods=['GET'])
def get_current_subscription():
    """Obtener suscripción actual del usuario"""
    try:
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'No autenticado'
            }), 401
        
        user_id = session['user_id']
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Buscar suscripción activa
        cursor.execute("""
            SELECT plan_name, start_date, end_date, status, payment_id
            FROM subscriptions
            WHERE user_id = ? AND status = 'active'
            ORDER BY end_date DESC
            LIMIT 1
        """, (user_id,))
        
        row = cursor.fetchone()
        
        if row:
            plan_name, start_date, end_date, status, payment_id = row
            
            # Calcular días restantes
            end_dt = datetime.fromisoformat(end_date)
            now = datetime.now()
            days_remaining = (end_dt - now).days
            
            # Obtener datos del plan
            plan_data = PLANS.get(plan_name, PLANS['free_trial'])
            
            return jsonify({
                'success': True,
                'subscription': {
                    'plan_name': plan_name,
                    'display_name': plan_data['display_name'],
                    'start_date': start_date,
                    'end_date': end_date,
                    'days_remaining': max(0, days_remaining),
                    'status': status,
                    'payment_id': payment_id
                }
            })
        else:
            return jsonify({
                'success': True,
                'subscription': None
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        if conn:
            conn.close()

@subscription_bp.route('/usage', methods=['GET'])
def get_usage():
    """Obtener uso actual y límites del usuario"""
    try:
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'No autenticado'
            }), 401
        
        user_id = session['user_id']
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Obtener suscripción activa para conocer límites
        cursor.execute("""
            SELECT plan_name
            FROM subscriptions
            WHERE user_id = ? AND status = 'active'
            ORDER BY end_date DESC
            LIMIT 1
        """, (user_id,))
        
        row = cursor.fetchone()
        plan_name = row[0] if row else 'free_trial'
        plan_limits = PLANS.get(plan_name, PLANS['free_trial'])['limits']
        
        # Contar backtests (último mes)
        cursor.execute("""
            SELECT COUNT(*) FROM backtest_results
            WHERE user_id = ? AND created_at > datetime('now', '-30 days')
        """, (user_id,))
        backtests_count = cursor.fetchone()[0] or 0
        
        # Contar signal bots
        cursor.execute("""
            SELECT COUNT(*) FROM signal_bots
            WHERE user_id = ?
        """, (user_id,))
        signal_bots_count = cursor.fetchone()[0] or 0
        
        # Contar auto bots
        cursor.execute("""
            SELECT COUNT(*) FROM auto_bots
            WHERE user_id = ?
        """, (user_id,))
        auto_bots_count = cursor.fetchone()[0] or 0
        
        # Contar estrategias guardadas
        cursor.execute("""
            SELECT COUNT(*) FROM strategies
            WHERE user_id = ?
        """, (user_id,))
        strategies_count = cursor.fetchone()[0] or 0
        
        return jsonify({
            'success': True,
            'usage': {
                'backtests': backtests_count,
                'signal_bots': signal_bots_count,
                'auto_bots': auto_bots_count,
                'strategies': strategies_count
            },
            'limits': plan_limits
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        if conn:
            conn.close()

@subscription_bp.route('/subscribe', methods=['POST'])
def subscribe():
    """Activar una suscripción"""
    try:
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'No autenticado'
            }), 401
        
        user_id = session['user_id']
        data = request.get_json()
        
        plan_name = data.get('plan_name')
        payment_id = data.get('payment_id', 'free_trial')
        payment_method = data.get('payment_method', 'free')
        
        if plan_name not in PLANS:
            return jsonify({
                'success': False,
                'error': 'Plan no válido'
            }), 400
        
        plan = PLANS[plan_name]
        
        # Validar que si es plan de pago, tiene payment_id
        if plan['price'] > 0 and payment_id == 'free_trial':
            return jsonify({
                'success': False,
                'error': 'Se requiere pago para este plan'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar si ya tiene una suscripción activa
        cursor.execute("""
            SELECT id FROM subscriptions
            WHERE user_id = ? AND status = 'active'
        """, (user_id,))
        
        if cursor.fetchone():
            # Desactivar suscripción anterior
            cursor.execute("""
                UPDATE subscriptions
                SET status = 'cancelled'
                WHERE user_id = ? AND status = 'active'
            """, (user_id,))
        
        # Crear nueva suscripción
        start_date = datetime.now()
        end_date = start_date + timedelta(days=plan['duration_days'])
        
        cursor.execute("""
            INSERT INTO subscriptions (user_id, plan_name, start_date, end_date, status, payment_id, payment_method)
            VALUES (?, ?, ?, ?, 'active', ?, ?)
        """, (user_id, plan_name, start_date.isoformat(), end_date.isoformat(), payment_id, payment_method))
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'Suscripción activada correctamente',
            'subscription': {
                'plan_name': plan_name,
                'display_name': plan['display_name'],
                'end_date': end_date.isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        if conn:
            conn.close()

@subscription_bp.route('/check-limit/<limit_type>', methods=['GET'])
def check_limit(limit_type):
    """Verificar si el usuario ha alcanzado un límite"""
    try:
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'No autenticado'
            }), 401
        
        user_id = session['user_id']
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print(f"🔍 [DEBUG] check_limit({limit_type}) - user_id: {user_id}")
        
        # Obtener plan actual
        cursor.execute("""
            SELECT plan_name
            FROM subscriptions
            WHERE user_id = ? AND status = 'active'
            ORDER BY end_date DESC
            LIMIT 1
        """, (user_id,))
        
        row = cursor.fetchone()
        
        print(f"🔍 [DEBUG] Plan encontrado: {row[0] if row else 'NINGUNO'}")
        
        # Si no tiene plan activo, bloquear todo
        if not row:
            conn.close()
            return jsonify({
                'success': True,
                'allowed': False,
                'limit': 0,
                'current': 0,
                'reason': f'No tienes un plan activo. Suscríbete para usar {limit_type}.'
            })
        
        plan_name = row[0]
        plan_limits = PLANS.get(plan_name, PLANS['free_trial'])['limits']
        
        # Mapear nombres de tipo de límite (singular a plural)
        limit_mapping = {
            'backtest': 'backtests',
            'signal_bot': 'signal_bots',
            'auto_bot': 'auto_bots',
            'strategy': 'strategies'
        }
        
        # Obtener la clave correcta del límite
        limit_key = limit_mapping.get(limit_type, limit_type)
        limit_value = plan_limits.get(limit_key, 0)
        
        print(f"🔍 [DEBUG] limit_type={limit_type}, limit_key={limit_key}, limit_value={limit_value}")
        
        # Si es ilimitado (-1), permitir
        if limit_value == -1:
            return jsonify({
                'success': True,
                'allowed': True,
                'limit': -1,
                'current': 0
            })
        
        # Contar uso actual según el tipo
        current_count = 0
        
        if limit_key == 'backtests':
            cursor.execute("""
                SELECT COUNT(*) FROM backtest_results
                WHERE user_id = ? AND created_at > datetime('now', '-30 days')
            """, (user_id,))
            current_count = cursor.fetchone()[0] or 0
        
        elif limit_key == 'signal_bots':
            cursor.execute("""
                SELECT COUNT(*) FROM signal_bots
                WHERE user_id = ?
            """, (user_id,))
            current_count = cursor.fetchone()[0] or 0
        
        elif limit_key == 'auto_bots':
            cursor.execute("""
                SELECT COUNT(*) FROM auto_bots
                WHERE user_id = ?
            """, (user_id,))
            current_count = cursor.fetchone()[0] or 0
        
        elif limit_key == 'strategies':
            cursor.execute("""
                SELECT COUNT(*) FROM strategies
                WHERE user_id = ?
            """, (user_id,))
            current_count = cursor.fetchone()[0] or 0
        
        allowed = current_count < limit_value
        
        print(f"🔍 [DEBUG] Límite: {limit_value}, Uso actual: {current_count}, Permitido: {allowed}")
        
        # Generar mensaje descriptivo si no está permitido
        reason = None
        if not allowed:
            type_names = {
                'backtests': 'backtests',
                'signal_bots': 'Signal Bots',
                'auto_bots': 'Auto Trading Bots',
                'strategies': 'estrategias guardadas'
            }
            reason = f'Has alcanzado el límite de {type_names.get(limit_type, limit_type)} de tu plan ({limit_value}). Actualiza tu plan para continuar.'
        
        response = {
            'success': True,
            'allowed': allowed,
            'limit': limit_value,
            'current': current_count,
            'remaining': max(0, limit_value - current_count)
        }
        
        if reason:
            response['reason'] = reason
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        if conn:
            conn.close()

@subscription_bp.route('/cancel', methods=['POST'])
def cancel_subscription():
    """Cancelar suscripción actual"""
    try:
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'No autenticado'
            }), 401
        
        user_id = session['user_id']
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE subscriptions
            SET status = 'cancelled'
            WHERE user_id = ? AND status = 'active'
        """, (user_id,))
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'Suscripción cancelada'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        if conn:
            conn.close()

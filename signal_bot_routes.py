"""
Signal Bot API Routes
Maneja todas las operaciones CRUD de los bots de señales
"""

from flask import Blueprint, request, jsonify, session
from database import get_db_connection
import json
import requests
from datetime import datetime
from bot_engine import BotEngine

signal_bot_bp = Blueprint('signal_bot', __name__)

# Instancia global del motor de bots
bot_engine = BotEngine()

@signal_bot_bp.route('/api/signal-bots/create', methods=['POST'])
def create_bot():
    """Crear un nuevo bot de señales"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        user_id = session['user_id']
        
        # Validar datos requeridos
        required_fields = ['name', 'symbol', 'timeframe', 'check_interval', 'strategy']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Bot token y chat_id son opcionales
        bot_token = data.get('bot_token', '')
        chat_id = data.get('chat_id', '')
        ignore_position_tracking = data.get('ignore_position_tracking', False)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar si la tabla existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='signal_bots'")
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'error': 'Database tables not initialized. Run update_database_bots.py first'
            }), 500
        
        # Insertar bot en la base de datos
        cursor.execute('''
            INSERT INTO signal_bots 
            (user_id, name, bot_token, chat_id, symbol, timeframe, check_interval, strategy, ignore_position_tracking, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'paused', ?)
        ''', (
            user_id,
            data['name'],
            bot_token,
            chat_id,
            data['symbol'],
            data['timeframe'],
            data['check_interval'],
            json.dumps(data['strategy']),
            1 if ignore_position_tracking else 0,
            datetime.now().isoformat()
        ))
        
        bot_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'bot_id': bot_id,
            'message': 'Bot created successfully'
        }), 201
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"❌ Error creating bot: {e}")
        print(f"Stack trace:\n{error_detail}")
        return jsonify({'error': str(e), 'detail': error_detail}), 500


@signal_bot_bp.route('/api/signal-bots/list', methods=['GET'])
def list_bots():
    """Listar todos los bots del usuario"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        user_id = session['user_id']
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, bot_token, chat_id, symbol, timeframe, check_interval, 
                   strategy, status, signals_sent, uptime, last_signal, last_signal_text, created_at, ignore_position_tracking
            FROM signal_bots
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
        
        bots = []
        for row in cursor.fetchall():
            bots.append({
                'id': f"bot_{row[0]}",
                'name': row[1],
                'bot_token': row[2],
                'chat_id': row[3],
                'symbol': row[4],
                'timeframe': row[5],
                'check_interval': row[6],
                'strategy': json.loads(row[7]) if row[7] else {},
                'status': row[8],
                'signals_sent': row[9] or 0,
                'uptime': row[10] or 0,
                'last_signal': row[11],
                'last_signal_text': row[12],
                'created_at': row[13],
                'ignore_position_tracking': bool(row[14]) if len(row) > 14 else False
            })
        
        conn.close()
        return jsonify(bots), 200
        
    except Exception as e:
        print(f"Error listing bots: {e}")
        return jsonify({'error': str(e)}), 500


@signal_bot_bp.route('/api/signal-bots/get/<bot_id>', methods=['GET'])
def get_bot(bot_id):
    """Obtener información de un bot específico"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Manejar diferentes formatos de ID:
        # - bot_6 (del servidor, válido)
        # - bot_1736429846_abc123 (localStorage, no válido)
        # - 6 (ID numérico directo, válido)
        
        numeric_id = None
        
        if bot_id.startswith('bot_'):
            after_prefix = bot_id[4:]  # Quitar "bot_"
            # Si tiene más guiones bajos o más de 10 dígitos, es un bot local
            if '_' in after_prefix or len(after_prefix) > 10:
                return jsonify({
                    'error': 'Bot only in localStorage',
                    'message': 'This bot is stored locally and hasn\'t been synced to the database yet.'
                }), 404
            # Es formato bot_6, extraer el número
            numeric_id = int(after_prefix)
        else:
            # Es un número directo
            numeric_id = int(bot_id)
        
        user_id = session['user_id']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, bot_token, chat_id, symbol, timeframe, check_interval, 
                   strategy, status, signals_sent, uptime, last_signal, last_signal_text, created_at
            FROM signal_bots
            WHERE id = ? AND user_id = ?
        ''', (numeric_id, user_id))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'error': 'Bot not found'}), 404
        
        bot = {
            'id': f"bot_{row[0]}",
            'name': row[1],
            'bot_token': row[2],
            'chat_id': row[3],
            'symbol': row[4],
            'timeframe': row[5],
            'check_interval': row[6],
            'strategy': json.loads(row[7]) if row[7] else {},
            'status': row[8],
            'signals_sent': row[9] or 0,
            'uptime': row[10] or 0,
            'last_signal': row[11],
            'last_signal_text': row[12],
            'created_at': row[13]
        }
        
        return jsonify(bot), 200
        
    except Exception as e:
        print(f"Error getting bot: {e}")
        return jsonify({'error': str(e)}), 500


@signal_bot_bp.route('/api/signal-bots/update/<bot_id>', methods=['PUT'])
def update_bot(bot_id):
    """Actualizar configuración de un bot"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        numeric_id = int(bot_id.replace('bot_', ''))
        user_id = session['user_id']
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar que el bot pertenece al usuario
        cursor.execute('SELECT id FROM signal_bots WHERE id = ? AND user_id = ?', (numeric_id, user_id))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Bot not found'}), 404
        
        # Actualizar bot
        cursor.execute('''
            UPDATE signal_bots
            SET name = ?, bot_token = ?, chat_id = ?, symbol = ?, 
                timeframe = ?, check_interval = ?, strategy = ?, ignore_position_tracking = ?
            WHERE id = ? AND user_id = ?
        ''', (
            data['name'],
            data['bot_token'],
            data['chat_id'],
            data['symbol'],
            data['timeframe'],
            data['check_interval'],
            json.dumps(data['strategy']),
            1 if data.get('ignore_position_tracking', False) else 0,
            numeric_id,
            user_id
        ))
        
        conn.commit()
        conn.close()
        
        # Si el bot está activo, reiniciarlo con la nueva configuración
        if data.get('status') == 'active':
            bot_engine.restart_bot(bot_id)
        
        return jsonify({'success': True, 'message': 'Bot updated successfully'}), 200
        
    except Exception as e:
        print(f"Error updating bot: {e}")
        return jsonify({'error': str(e)}), 500


@signal_bot_bp.route('/api/signal-bots/delete/<bot_id>', methods=['DELETE'])
def delete_bot(bot_id):
    """Eliminar un bot"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        user_id = session['user_id']
        
        # Detener el bot si está activo
        bot_engine.stop_bot(bot_id)
        
        # Intentar convertir a ID numérico si es posible
        try:
            if bot_id.startswith('bot_'):
                numeric_part = bot_id.replace('bot_', '').split('_')[0]
                numeric_id = int(numeric_part)
            else:
                numeric_id = int(bot_id)
        except (ValueError, AttributeError):
            # Si no se puede convertir, el bot solo existe localmente
            return jsonify({
                'success': True, 
                'message': 'Bot deleted locally (was not in database)'
            }), 200
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Eliminar señales asociadas
        cursor.execute('DELETE FROM bot_signals WHERE bot_id = ?', (numeric_id,))
        
        # Eliminar bot
        cursor.execute('DELETE FROM signal_bots WHERE id = ? AND user_id = ?', (numeric_id, user_id))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Bot not found'}), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Bot deleted successfully'}), 200
        
    except Exception as e:
        print(f"Error deleting bot: {e}")
        return jsonify({'error': str(e)}), 500


@signal_bot_bp.route('/api/signal-bots/activate/<bot_id>', methods=['POST'])
def activate_bot(bot_id):
    """Activar un bot"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        user_id = session['user_id']
        
        # Intentar convertir a ID numérico si es posible
        try:
            # Si el bot_id es numérico o tiene formato bot_NUMERO
            if bot_id.startswith('bot_'):
                numeric_part = bot_id.replace('bot_', '').split('_')[0]
                numeric_id = int(numeric_part)
            else:
                numeric_id = int(bot_id)
        except (ValueError, AttributeError):
            # Si no se puede convertir, el bot no está en la base de datos
            return jsonify({
                'error': 'Bot not found in database',
                'message': 'This bot only exists locally. Create it first using the "Create Bot" button.'
            }), 404
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar que el bot existe y obtener su configuración
        cursor.execute('''
            SELECT id, name, bot_token, chat_id, symbol, timeframe, check_interval, strategy
            FROM signal_bots
            WHERE id = ? AND user_id = ?
        ''', (numeric_id, user_id))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return jsonify({'error': 'Bot not found'}), 404
        
        # Actualizar estado en la base de datos
        cursor.execute('UPDATE signal_bots SET status = ? WHERE id = ?', ('active', numeric_id))
        conn.commit()
        conn.close()
        
        # Iniciar el bot en el motor
        bot_config = {
            'id': f'bot_{numeric_id}',  # CORREGIDO: usar formato bot_NUMERO consistente
            'name': row[1],
            'bot_token': row[2],
            'chat_id': row[3],
            'symbol': row[4],
            'timeframe': row[5],
            'check_interval': row[6],
            'strategy': json.loads(row[7]) if row[7] else {}
        }
        
        success = bot_engine.start_bot(bot_config)
        
        if success:
            print(f"✅ Bot {bot_config['name']} started for {bot_config['symbol']} on {bot_config['timeframe']}")
            return jsonify({'success': True, 'message': 'Bot activated successfully'}), 200
        else:
            return jsonify({'error': 'Failed to start bot in engine'}), 500
        
    except Exception as e:
        print(f"Error activating bot: {e}")
        return jsonify({'error': str(e)}), 500


@signal_bot_bp.route('/api/signal-bots/pause/<bot_id>', methods=['POST'])
def pause_bot(bot_id):
    """Pausar un bot"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        user_id = session['user_id']
        
        # Intentar convertir a ID numérico si es posible
        try:
            if bot_id.startswith('bot_'):
                numeric_part = bot_id.replace('bot_', '').split('_')[0]
                numeric_id = int(numeric_part)
            else:
                numeric_id = int(bot_id)
        except (ValueError, AttributeError):
            # Si no se puede convertir, el bot no está en la base de datos
            return jsonify({
                'error': 'Bot not found in database',
                'message': 'This bot only exists locally.'
            }), 404
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar que el bot existe
        cursor.execute('SELECT id FROM signal_bots WHERE id = ? AND user_id = ?', (numeric_id, user_id))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Bot not found'}), 404
        
        # Actualizar estado en la base de datos
        cursor.execute('UPDATE signal_bots SET status = ? WHERE id = ?', ('paused', numeric_id))
        conn.commit()
        conn.close()
        
        # Detener el bot en el motor con el ID correcto
        bot_engine.stop_bot(f'bot_{numeric_id}')
        
        print(f"⏸️ Bot bot_{numeric_id} paused")
        return jsonify({'success': True, 'message': 'Bot paused successfully'}), 200
        
    except Exception as e:
        print(f"Error pausing bot: {e}")
        return jsonify({'error': str(e)}), 500


@signal_bot_bp.route('/api/signal-bots/toggle-tracking/<bot_id>', methods=['POST'])
def toggle_bot_tracking(bot_id):
    """Cambiar modo de tracking de posiciones (Profesional/Prueba)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        user_id = session['user_id']
        data = request.get_json()
        ignore_tracking = data.get('ignore_tracking', False)
        
        # Intentar convertir a ID numérico si es posible
        try:
            if bot_id.startswith('bot_'):
                numeric_part = bot_id.replace('bot_', '').split('_')[0]
                numeric_id = int(numeric_part)
            else:
                numeric_id = int(bot_id)
        except (ValueError, AttributeError):
            return jsonify({
                'error': 'Bot not found in database',
                'message': 'This bot only exists locally.'
            }), 404
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar que el bot existe y pertenece al usuario
        cursor.execute('SELECT id FROM signal_bots WHERE id = ? AND user_id = ?', (numeric_id, user_id))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Bot not found'}), 404
        
        # Actualizar en la base de datos
        cursor.execute(
            'UPDATE signal_bots SET ignore_position_tracking = ? WHERE id = ?',
            (1 if ignore_tracking else 0, numeric_id)
        )
        conn.commit()
        conn.close()
        
        # Actualizar el bot en ejecución si existe
        full_bot_id = f'bot_{numeric_id}'
        if full_bot_id in bot_engine.bots:
            bot_engine.bots[full_bot_id].toggle_position_tracking(ignore_tracking)
        
        mode = "Prueba (ignora tracking)" if ignore_tracking else "Profesional (respeta tracking)"
        print(f"🎚️ Bot {full_bot_id} cambió a modo: {mode}")
        
        return jsonify({
            'success': True,
            'message': f'Modo cambiado a: {mode}',
            'ignore_tracking': ignore_tracking
        }), 200
        
    except Exception as e:
        print(f"Error toggling tracking mode: {e}")
        return jsonify({'error': str(e)}), 500


@signal_bot_bp.route('/api/signal-bots/health', methods=['GET'])
def health_check():
    """Endpoint de diagnóstico del sistema"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        signal_bots_exists = 'signal_bots' in tables
        bot_signals_exists = 'bot_signals' in tables
        
        bot_count = 0
        signal_count = 0
        
        if signal_bots_exists:
            cursor.execute("SELECT COUNT(*) FROM signal_bots")
            bot_count = cursor.fetchone()[0]
        
        if bot_signals_exists:
            cursor.execute("SELECT COUNT(*) FROM bot_signals")
            signal_count = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'status': 'ok',
            'database': {
                'connected': True,
                'tables': {
                    'signal_bots': signal_bots_exists,
                    'bot_signals': bot_signals_exists
                },
                'counts': {
                    'bots': bot_count,
                    'signals': signal_count
                }
            },
            'bot_engine': {
                'active_bots': len(bot_engine.bots)
            }
        }), 200
        
    except Exception as e:
        import traceback
        return jsonify({
            'status': 'error',
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


# ==================== TELEGRAM API ENDPOINTS ====================

@signal_bot_bp.route('/api/telegram/get-chat-id', methods=['POST'])
def get_telegram_chat_id():
    """Obtener el Chat ID desde el bot de Telegram"""
    try:
        data = request.get_json()
        bot_token = data.get('bot_token', '').strip()
        
        if not bot_token:
            return jsonify({'error': 'Bot token is required'}), 400
        
        # Llamar a la API de Telegram para obtener actualizaciones
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        
        if not result.get('ok'):
            return jsonify({
                'error': 'Invalid bot token or Telegram API error',
                'description': result.get('description', 'Unknown error')
            }), 400
        
        updates = result.get('result', [])
        
        if not updates:
            return jsonify({
                'error': 'No messages found',
                'message': 'Send any message to the bot first, then try again'
            }), 404
        
        # Obtener el chat_id del último mensaje
        last_update = updates[-1]
        chat_id = None
        
        if 'message' in last_update:
            chat_id = last_update['message']['chat']['id']
        elif 'channel_post' in last_update:
            chat_id = last_update['channel_post']['chat']['id']
        
        if not chat_id:
            return jsonify({
                'error': 'Could not extract chat_id',
                'message': 'Send a message to the bot first'
            }), 404
        
        return jsonify({
            'success': True,
            'chat_id': str(chat_id),
            'message': 'Chat ID obtained successfully'
        }), 200
        
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': 'Network error connecting to Telegram',
            'detail': str(e)
        }), 500
    except Exception as e:
        return jsonify({
            'error': 'Error getting chat ID',
            'detail': str(e)
        }), 500


@signal_bot_bp.route('/api/telegram/send-test', methods=['POST'])
def send_telegram_test_message():
    """Enviar mensaje de prueba a Telegram"""
    try:
        data = request.get_json()
        bot_token = data.get('bot_token', '').strip()
        chat_id = data.get('chat_id', '').strip()
        
        if not bot_token or not chat_id:
            return jsonify({'error': 'Bot token and chat_id are required'}), 400
        
        # Mensaje de prueba
        test_message = """
🤖 <b>DragLab Signal Bot - Test Message</b>

✅ Connection successful!
📡 Your bot is correctly configured.

You will receive trading signals here when the bot is active.

<i>Test sent at: {}</i>
        """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # Enviar mensaje
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        payload = {
            'chat_id': chat_id,
            'text': test_message,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        
        if result.get('ok'):
            return jsonify({
                'success': True,
                'message': 'Test message sent successfully'
            }), 200
        else:
            return jsonify({
                'error': 'Failed to send message',
                'description': result.get('description', 'Unknown error')
            }), 400
        
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': 'Network error connecting to Telegram',
            'detail': str(e)
        }), 500
    except Exception as e:
        return jsonify({
            'error': 'Error sending test message',
            'detail': str(e)
        }), 500


# ==================== BOT MONITORING ENDPOINTS ====================

@signal_bot_bp.route('/api/signal-bots/logs/<bot_id>', methods=['GET'])
def get_bot_logs(bot_id):
    """Obtener logs de actividad del bot"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        user_id = session['user_id']
        
        # Intentar convertir a ID numérico
        try:
            if bot_id.startswith('bot_'):
                numeric_part = bot_id.replace('bot_', '').split('_')[0]
                numeric_id = int(numeric_part)
            else:
                numeric_id = int(bot_id)
        except (ValueError, AttributeError):
            return jsonify({
                'error': 'Bot not found in database',
                'logs': []
            }), 404
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar que el bot pertenece al usuario
        cursor.execute('SELECT id, name FROM signal_bots WHERE id = ? AND user_id = ?', (numeric_id, user_id))
        bot_row = cursor.fetchone()
        
        if not bot_row:
            conn.close()
            return jsonify({'error': 'Bot not found'}), 404
        
        # Obtener señales/logs recientes (últimas 50)
        cursor.execute('''
            SELECT id, signal_type, signal_text, created_at
            FROM bot_signals
            WHERE bot_id = ?
            ORDER BY created_at DESC
            LIMIT 50
        ''', (numeric_id,))
        
        signals = []
        for row in cursor.fetchall():
            signals.append({
                'id': row[0],
                'type': row[1],
                'text': row[2],
                'timestamp': row[3]
            })
        
        conn.close()
        
        # Obtener estado del bot en el motor
        bot_status = bot_engine.get_bot_status(bot_id)
        
        return jsonify({
            'success': True,
            'bot_name': bot_row[1],
            'logs': signals,
            'bot_status': bot_status
        }), 200
        
    except Exception as e:
        print(f"Error getting bot logs: {e}")
        return jsonify({'error': str(e)}), 500


@signal_bot_bp.route('/api/signal-bots/check-now/<bot_id>', methods=['POST'])
def force_check_now(bot_id):
    """Forzar verificación inmediata del mercado"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        user_id = session['user_id']
        
        # Verificar que el bot existe y está activo
        try:
            if bot_id.startswith('bot_'):
                numeric_part = bot_id.replace('bot_', '').split('_')[0]
                numeric_id = int(numeric_part)
            else:
                numeric_id = int(bot_id)
        except (ValueError, AttributeError):
            return jsonify({
                'error': 'Bot not found in database',
                'message': 'This bot only exists locally.'
            }), 404
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, status
            FROM signal_bots
            WHERE id = ? AND user_id = ?
        ''', (numeric_id, user_id))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'error': 'Bot not found'}), 404
        
        if row[2] != 'active':
            return jsonify({
                'error': 'Bot is not active',
                'message': 'Activate the bot first before forcing a check'
            }), 400
        
        # Forzar verificación en el motor del bot
        result = bot_engine.force_check(bot_id)
        
        if result:
            return jsonify({
                'success': True,
                'message': 'Market check completed successfully',
                'result': result
            }), 200
        else:
            return jsonify({
                'error': 'Bot is not running',
                'message': 'The bot might have stopped or crashed. Try reactivating it.'
            }), 400
        
    except Exception as e:
        print(f"Error forcing check: {e}")
        return jsonify({'error': str(e)}), 500


@signal_bot_bp.route('/api/signal-bots/status/<bot_id>', methods=['GET'])
def get_bot_status_detailed(bot_id):
    """Obtener estado detallado del bot"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        user_id = session['user_id']
        
        # Intentar convertir a ID numérico
        try:
            if bot_id.startswith('bot_'):
                numeric_part = bot_id.replace('bot_', '').split('_')[0]
                numeric_id = int(numeric_part)
            else:
                numeric_id = int(bot_id)
        except (ValueError, AttributeError):
            return jsonify({
                'error': 'Bot not found in database',
                'status': 'unknown'
            }), 404
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, symbol, timeframe, check_interval, status, 
                   signals_sent, uptime, last_signal, last_signal_text
            FROM signal_bots
            WHERE id = ? AND user_id = ?
        ''', (numeric_id, user_id))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'error': 'Bot not found'}), 404
        
        # Obtener estado en tiempo real del motor
        bot_status = bot_engine.get_bot_status(bot_id)
        
        return jsonify({
            'success': True,
            'bot_id': bot_id,
            'name': row[1],
            'symbol': row[2],
            'timeframe': row[3],
            'check_interval': row[4],
            'status': row[5],
            'signals_sent': row[6] or 0,
            'uptime': row[7] or 0,
            'last_signal': row[8],
            'last_signal_text': row[9],
            'engine_status': bot_status
        }), 200
        
    except Exception as e:
        print(f"Error getting bot status: {e}")
        return jsonify({'error': str(e)}), 500

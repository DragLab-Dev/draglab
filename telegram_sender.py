"""
Telegram Sender
Envía mensajes y señales a canales/grupos de Telegram
"""

import requests
from typing import Optional

class TelegramSender:
    """Manejador de envío de mensajes a Telegram"""
    
    def __init__(self, bot_token: str, chat_id: str):
        """
        Inicializar el sender de Telegram
        
        Args:
            bot_token: Token del bot de Telegram
            chat_id: ID del chat/canal donde enviar mensajes
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_message(self, text: str, parse_mode: str = 'HTML', disable_notification: bool = False) -> bool:
        """
        Enviar un mensaje de texto a Telegram
        
        Args:
            text: Texto del mensaje
            parse_mode: Modo de parseo ('HTML' o 'Markdown')
            disable_notification: Si es True, envía el mensaje sin notificación
        
        Returns:
            True si se envió exitosamente, False en caso contrario
        """
        try:
            url = f"{self.base_url}/sendMessage"
            
            payload = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': parse_mode,
                'disable_notification': disable_notification
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('ok'):
                print(f"✅ Message sent successfully to chat {self.chat_id}")
                return True
            else:
                print(f"❌ Failed to send message: {result.get('description', 'Unknown error')}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error sending message: {e}")
            return False
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return False
    
    def send_photo(self, photo_url: str, caption: Optional[str] = None) -> bool:
        """
        Enviar una foto a Telegram
        
        Args:
            photo_url: URL de la foto
            caption: Texto de descripción opcional
        
        Returns:
            True si se envió exitosamente, False en caso contrario
        """
        try:
            url = f"{self.base_url}/sendPhoto"
            
            payload = {
                'chat_id': self.chat_id,
                'photo': photo_url
            }
            
            if caption:
                payload['caption'] = caption
                payload['parse_mode'] = 'HTML'
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('ok'):
                print(f"✅ Photo sent successfully to chat {self.chat_id}")
                return True
            else:
                print(f"❌ Failed to send photo: {result.get('description', 'Unknown error')}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error sending photo: {e}")
            return False
        except Exception as e:
            print(f"❌ Error sending photo: {e}")
            return False
    
    def test_connection(self) -> bool:
        """
        Probar la conexión con Telegram y verificar que el bot tenga acceso al chat
        
        Returns:
            True si la conexión es exitosa, False en caso contrario
        """
        try:
            # Primero verificar que el bot token sea válido
            url = f"{self.base_url}/getMe"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            result = response.json()
            
            if not result.get('ok'):
                print(f"❌ Invalid bot token")
                return False
            
            bot_info = result.get('result', {})
            print(f"✅ Bot authenticated: @{bot_info.get('username')}")
            
            # Intentar enviar un mensaje de prueba
            test_message = "🤖 Bot conectado exitosamente"
            return self.send_message(test_message, disable_notification=True)
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error testing connection: {e}")
            return False
        except Exception as e:
            print(f"❌ Error testing connection: {e}")
            return False
    
    def format_signal_message(self, signal_data: dict) -> str:
        """
        Formatear un mensaje de señal con estilo
        
        Args:
            signal_data: Diccionario con datos de la señal
        
        Returns:
            Mensaje formateado en HTML
        """
        symbol = signal_data.get('symbol', 'UNKNOWN')
        signal_type = signal_data.get('type', 'SIGNAL')
        price = signal_data.get('price', 0.0)
        timestamp = signal_data.get('timestamp', '')
        
        # Emoji según el tipo de señal
        if 'LONG' in signal_type.upper() or 'BUY' in signal_type.upper():
            emoji = '🟢'
            color = 'LONG'
        elif 'SHORT' in signal_type.upper() or 'SELL' in signal_type.upper():
            emoji = '🔴'
            color = 'SHORT'
        else:
            emoji = '⚪'
            color = 'NEUTRAL'
        
        message = f"""
{emoji} <b>SEÑAL DE TRADING</b> {emoji}

━━━━━━━━━━━━━━━━━
📊 <b>Par:</b> {symbol}
📈 <b>Tipo:</b> {signal_type}
💰 <b>Precio:</b> ${price:,.2f}
🕐 <b>Hora:</b> {timestamp}
━━━━━━━━━━━━━━━━━

💡 <i>Señal generada automáticamente</i>
⚠️ <i>Haz tu propio análisis antes de operar</i>
        """
        
        return message.strip()

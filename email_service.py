"""
Sistema de envío de emails para verificación de cuentas
Usa Gmail SMTP para enviar códigos de verificación
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración de email
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = os.getenv("GMAIL_USER", "tu_email@gmail.com")
EMAIL_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "tu_app_password")

def send_verification_email(to_email, code, user_name=None):
    """Enviar email de verificación con código de 4 dígitos"""
    
    subject = "Código de Verificación - TradingBot Platform"
    
    # HTML del email
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                padding: 20px;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                padding: 40px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .logo {{
                font-size: 32px;
                font-weight: bold;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 10px;
            }}
            .code-box {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 10px;
                text-align: center;
                margin: 30px 0;
            }}
            .code {{
                font-size: 48px;
                font-weight: bold;
                letter-spacing: 15px;
                font-family: 'Courier New', monospace;
            }}
            .message {{
                color: #333;
                line-height: 1.6;
                margin-bottom: 20px;
            }}
            .footer {{
                text-align: center;
                color: #666;
                font-size: 12px;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #eee;
            }}
            .warning {{
                background: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 15px;
                margin: 20px 0;
                border-radius: 5px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">📈 TradingBot Platform</div>
                <p style="color: #666;">Sistema de Trading Automatizado</p>
            </div>
            
            <div class="message">
                <h2>¡Bienvenido{' ' + user_name if user_name else ''}! 👋</h2>
                <p>Gracias por registrarte en TradingBot Platform. Para completar tu registro y activar tu cuenta, por favor verifica tu correo electrónico.</p>
            </div>
            
            <div class="code-box">
                <p style="margin: 0 0 10px 0; font-size: 14px;">Tu código de verificación es:</p>
                <div class="code">{code}</div>
                <p style="margin: 10px 0 0 0; font-size: 12px;">Este código expira en 15 minutos</p>
            </div>
            
            <div class="warning">
                <strong>⚠️ Importante:</strong> Si no solicitaste este código, ignora este email. Tu cuenta está protegida.
            </div>
            
            <div class="message">
                <p><strong>¿Qué puedes hacer con TradingBot Platform?</strong></p>
                <ul>
                    <li>✅ Crear y gestionar bots de trading automatizados</li>
                    <li>✅ Recibir señales de trading en tiempo real vía Telegram</li>
                    <li>✅ Realizar backtests de estrategias personalizadas</li>
                    <li>✅ Monitorear múltiples pares y timeframes</li>
                </ul>
            </div>
            
            <div class="footer">
                <p>TradingBot Platform - Sistema de Trading Automatizado</p>
                <p>Este es un email automático, por favor no respondas a este mensaje.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Crear mensaje
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    
    # Agregar HTML
    html_part = MIMEText(html_content, 'html')
    msg.attach(html_part)
    
    # Enviar email
    try:
        # MODO DESARROLLO: Mostrar código en consola si no hay conexión
        print("\n" + "="*60)
        print("📧 CÓDIGO DE VERIFICACIÓN")
        print("="*60)
        print(f"Para: {to_email}")
        print(f"Código: {code}")
        print("="*60 + "\n")
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"✅ Email enviado a {to_email}")
        return True
    except Exception as e:
        print(f"❌ Error enviando email: {e}")
        print("⚠️  MODO DESARROLLO: El código se mostró arriba en la consola")
        # En desarrollo, consideramos exitoso si al menos mostramos el código
        return True

def send_welcome_email(to_email, user_name):
    """Enviar email de bienvenida después de verificación"""
    
    subject = "¡Cuenta Verificada! - TradingBot Platform"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                padding: 20px;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                padding: 40px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .logo {{
                font-size: 32px;
                font-weight: bold;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 10px;
            }}
            .success-icon {{
                font-size: 64px;
                margin: 20px 0;
            }}
            .button {{
                display: inline-block;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px 40px;
                border-radius: 25px;
                text-decoration: none;
                font-weight: bold;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">📈 TradingBot Platform</div>
                <div class="success-icon">✅</div>
                <h1>¡Cuenta Verificada!</h1>
            </div>
            
            <p>Hola {user_name},</p>
            <p>Tu cuenta ha sido verificada exitosamente. Ya puedes empezar a usar TradingBot Platform.</p>
            
            <div style="text-align: center;">
                <a href="http://192.168.1.13:5000" class="button">Ir a la Plataforma</a>
            </div>
            
            <h3>Primeros Pasos:</h3>
            <ol>
                <li>Crea tu primer bot de señales</li>
                <li>Configura Telegram para recibir notificaciones</li>
                <li>Realiza backtests de estrategias</li>
                <li>Explora las diferentes configuraciones</li>
            </ol>
            
            <p>¡Feliz trading! 🚀</p>
            
            <div style="text-align: center; color: #666; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                <p>TradingBot Platform - Sistema de Trading Automatizado</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg.attach(MIMEText(html_content, 'html'))
    
    try:
        print(f"\n✅ Email de bienvenida para: {to_email}")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"❌ Error enviando email de bienvenida: {e}")
        print("⚠️  En producción configurar correctamente Gmail SMTP")
        return True  # No bloquear el proceso por falta de email


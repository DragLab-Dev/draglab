# Visual Strategy Creator - Deployment Guide

## 🚀 Guía de Despliegue en VPS

**Visual Strategy Creator** es un constructor visual de estrategias de trading mediante bloques que permite crear bots y ejecutar backtests **sin necesidad de programar**.

Esta guía te ayudará a desplegar la aplicación en tu VPS paso a paso.

---

## 📋 Requisitos del VPS

- **OS**: Ubuntu 20.04 LTS o superior (recomendado)
- **RAM**: Mínimo 1GB (2GB recomendado)
- **CPU**: 1 core mínimo
- **Disco**: 10GB mínimo
- **Python**: 3.8 o superior
- **Puerto**: 80 (HTTP) y 443 (HTTPS)

---

## 🔧 Paso 1: Preparar el Servidor

```bash
# Conectar al VPS
ssh usuario@tu-ip-vps

# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias del sistema
sudo apt install -y python3 python3-pip python3-venv git nginx certbot python3-certbot-nginx

# Configurar firewall
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

---

## 📦 Paso 2: Clonar y Configurar

```bash
# Navegar al directorio de aplicaciones
cd /var/www

# Clonar repositorio
sudo git clone <tu-repositorio-url> visual-strategy-creator
cd visual-strategy-creator

# Dar permisos
sudo chown -R $USER:$USER /var/www/visual-strategy-creator

# Ejecutar instalador
chmod +x install.sh
./install.sh
```

---

## ⚙️ Paso 3: Configurar Variables de Entorno

```bash
# Editar archivo .env
nano .env
```

**Configuración mínima requerida:**

```env
SECRET_KEY=genera-una-clave-segura-aleatoria-aqui
GMAIL_USER=tu-email@gmail.com
GMAIL_APP_PASSWORD=tu-app-password-de-16-caracteres
GOOGLE_CLIENT_ID=tu-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=tu-google-client-secret
```

**Para generar SECRET_KEY:**

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## 🔐 Paso 4: Configurar Gmail App Password

1. Ve a https://myaccount.google.com/security
2. Activa "Verificación en 2 pasos"
3. Ve a https://myaccount.google.com/apppasswords
4. Genera una contraseña de aplicación
5. Copia el código de 16 caracteres a `GMAIL_APP_PASSWORD`

---

## 🌐 Paso 5: Configurar NGINX

```bash
# Crear configuración de NGINX
sudo nano /etc/nginx/sites-available/visual-strategy
```

**Contenido del archivo:**

```nginx
server {
    listen 80;
    server_name tu-dominio.com www.tu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (si lo necesitas)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Archivos estáticos (si los tienes)
    location /static {
        alias /var/www/visual-strategy-creator/static;
        expires 30d;
    }
}
```

**Activar configuración:**

```bash
# Crear enlace simbólico
sudo ln -s /etc/nginx/sites-available/visual-strategy /etc/nginx/sites-enabled/

# Verificar configuración
sudo nginx -t

# Reiniciar NGINX
sudo systemctl restart nginx
```

---

## 🐍 Paso 6: Configurar Gunicorn como Servicio

```bash
# Crear archivo de servicio systemd
sudo nano /etc/systemd/system/visual-strategy.service
```

**Contenido del archivo:**

```ini
[Unit]
Description=Visual Strategy Creator - Gunicorn
After=network.target

[Service]
Type=notify
User=tu-usuario-vps
Group=www-data
WorkingDirectory=/var/www/visual-strategy-creator
Environment="PATH=/var/www/visual-strategy-creator/venv/bin"
ExecStart=/var/www/visual-strategy-creator/venv/bin/gunicorn \
    --workers 3 \
    --bind 127.0.0.1:5000 \
    --timeout 120 \
    --access-logfile /var/log/visual-strategy/access.log \
    --error-logfile /var/log/visual-strategy/error.log \
    app:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Crear directorio de logs:**

```bash
sudo mkdir -p /var/log/visual-strategy
sudo chown -R $USER:www-data /var/log/visual-strategy
```

**Iniciar servicio:**

```bash
# Recargar systemd
sudo systemctl daemon-reload

# Iniciar servicio
sudo systemctl start visual-strategy

# Habilitar inicio automático
sudo systemctl enable visual-strategy

# Verificar estado
sudo systemctl status visual-strategy
```

---

## 🔒 Paso 7: Configurar SSL (HTTPS)

```bash
# Obtener certificado SSL gratuito con Let's Encrypt
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com

# Seguir las instrucciones del asistente
# Elige "2" para redirigir HTTP a HTTPS automáticamente

# Verificar renovación automática
sudo certbot renew --dry-run
```

---

## 📊 Paso 8: Crear Usuario Administrador

```bash
# Activar entorno virtual
cd /var/www/visual-strategy-creator
source venv/bin/activate

# Ejecutar Python
python3

# En el intérprete de Python:
>>> import database as db
>>> db.init_database()
>>> db.create_user("admin@tudominio.com", "ContraseñaSegura123!", is_admin=True)
>>> exit()
```

---

## 🎯 Comandos Útiles de Mantenimiento

```bash
# Ver logs en tiempo real
sudo journalctl -u visual-strategy -f

# Ver logs de error
tail -f /var/log/visual-strategy/error.log

# Ver logs de acceso
tail -f /var/log/visual-strategy/access.log

# Reiniciar servicio
sudo systemctl restart visual-strategy

# Detener servicio
sudo systemctl stop visual-strategy

# Ver estado del servicio
sudo systemctl status visual-strategy

# Reiniciar NGINX
sudo systemctl restart nginx

# Verificar NGINX
sudo nginx -t
```

---

## 🔄 Actualizar la Aplicación

```bash
# Navegar al directorio
cd /var/www/visual-strategy-creator

# Hacer backup de .env
cp .env .env.backup

# Pull de cambios
git pull origin main

# Activar entorno virtual
source venv/bin/activate

# Actualizar dependencias
pip install -r requirements.txt

# Restaurar .env
cp .env.backup .env

# Reiniciar servicio
sudo systemctl restart visual-strategy
```

---

## 🛡️ Seguridad Adicional

### 1. Configurar Fail2Ban (Protección contra ataques)

```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 2. Backup Automático de Base de Datos

```bash
# Crear script de backup
nano ~/backup-db.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp /var/www/visual-strategy-creator/database/tradingbot.db \
   ~/backups/tradingbot_$DATE.db
find ~/backups -name "tradingbot_*.db" -mtime +7 -delete
```

```bash
# Dar permisos y programar
chmod +x ~/backup-db.sh
mkdir -p ~/backups
crontab -e

# Agregar línea (backup diario a las 3 AM):
0 3 * * * /home/tu-usuario/backup-db.sh
```

---

## 🐛 Solución de Problemas

### Servicio no inicia

```bash
# Ver logs detallados
sudo journalctl -u visual-strategy -n 50 --no-pager

# Verificar permisos
ls -la /var/www/visual-strategy-creator
sudo chown -R $USER:www-data /var/www/visual-strategy-creator
```

### Error de conexión a base de datos

```bash
# Verificar permisos de database
chmod 755 /var/www/visual-strategy-creator/database
chmod 644 /var/www/visual-strategy-creator/database/tradingbot.db
```

### NGINX 502 Bad Gateway

```bash
# Verificar que Gunicorn esté corriendo
sudo systemctl status visual-strategy

# Reiniciar ambos servicios
sudo systemctl restart visual-strategy
sudo systemctl restart nginx
```

---

## 📞 Soporte

Si encuentras problemas durante el despliegue:

1. Revisa los logs del servicio
2. Verifica la configuración de .env
3. Comprueba los permisos de archivos
4. Contacta: camiloeagiraldodev@gmail.com

---

**¡Tu aplicación ya está en producción! 🎉**

Accede a: **https://tu-dominio.com**

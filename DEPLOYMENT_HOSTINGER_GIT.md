# 🚀 DEPLOYMENT EN HOSTINGER VPS CON GIT

## Paso 1: Preparar Git en Local (Windows)

### 1.1 Inicializar Repositorio Git

Abre PowerShell en la carpeta del proyecto:

```powershell
cd "C:\Users\Olga\Downloads\TradingBot\Visual strategy creator"

# Inicializar repositorio Git
git init

# Agregar todos los archivos (respeta .gitignore)
git add .

# Crear primer commit
git commit -m "Initial commit - Visual Strategy Creator"
```

### 1.2 Crear Repositorio en GitHub/GitLab (RECOMENDADO)

**Opción A: GitHub**
1. Ve a https://github.com/new
2. Nombre: `visual-strategy-creator`
3. Descripción: `Visual Strategy Builder - Trading Platform`
4. Privado: ✅ (para proteger tu código)
5. Click "Create repository"

**Opción B: GitLab**
1. Ve a https://gitlab.com/projects/new
2. Igual configuración que GitHub

### 1.3 Conectar con Repositorio Remoto

```powershell
# Conectar con GitHub (reemplaza con tu usuario)
git remote add origin https://github.com/TU_USUARIO/visual-strategy-creator.git

# O con GitLab
git remote add origin https://gitlab.com/TU_USUARIO/visual-strategy-creator.git

# Subir código
git branch -M main
git push -u origin main
```

---

## Paso 2: Conectar al VPS de Hostinger

### 2.1 Obtener Credenciales SSH de Hostinger

1. Entra a tu panel de Hostinger
2. Ve a **VPS** → **Tu VPS** → **Detalles del Servidor**
3. Anota:
   - **IP del servidor:** (ejemplo: 123.45.67.89)
   - **Usuario SSH:** (usualmente `root` o `u123456789`)
   - **Puerto SSH:** (usualmente `22`)

### 2.2 Conectar vía SSH

```powershell
# Desde PowerShell
ssh usuario@tu-ip-del-vps

# Ejemplo:
ssh root@123.45.67.89
# o
ssh u123456789@123.45.67.89
```

Si es la primera vez, te pedirá confirmar la huella digital del servidor (escribe `yes`).

---

## Paso 3: Configurar el VPS (Primera Vez)

Una vez conectado al VPS:

### 3.1 Actualizar Sistema

```bash
# Actualizar paquetes
sudo apt update && sudo apt upgrade -y

# Instalar herramientas necesarias
sudo apt install -y python3 python3-pip python3-venv git nginx supervisor
```

### 3.2 Configurar Git en el VPS

```bash
# Configurar Git
git config --global user.name "Tu Nombre"
git config --global user.email "tu@email.com"
```

### 3.3 Generar SSH Key para GitHub/GitLab (si el repo es privado)

```bash
# Generar clave SSH
ssh-keygen -t ed25519 -C "tu@email.com"

# Presiona Enter 3 veces (sin passphrase)

# Copiar la clave pública
cat ~/.ssh/id_ed25519.pub
```

**Agregar a GitHub/GitLab:**
- **GitHub:** Settings → SSH and GPG keys → New SSH key → Pegar la clave
- **GitLab:** Preferences → SSH Keys → Pegar la clave

---

## Paso 4: Clonar el Proyecto en el VPS

### 4.1 Crear Directorio Web

```bash
# Crear directorio para la aplicación
sudo mkdir -p /var/www/visual-strategy-creator
sudo chown $USER:$USER /var/www/visual-strategy-creator
cd /var/www/visual-strategy-creator
```

### 4.2 Clonar desde GitHub/GitLab

```bash
# Clonar repositorio
git clone git@github.com:TU_USUARIO/visual-strategy-creator.git .

# O con HTTPS (si no configuraste SSH)
git clone https://github.com/TU_USUARIO/visual-strategy-creator.git .
```

---

## Paso 5: Configurar el Proyecto

### 5.1 Ejecutar Script de Instalación

```bash
# Dar permisos de ejecución
chmod +x *.sh

# Ejecutar instalación
./install.sh
```

### 5.2 Configurar Variables de Entorno

```bash
# Editar .env
nano .env
```

**Actualiza estas variables:**

```env
# IMPORTANTE: Genera un nuevo SECRET_KEY para producción
SECRET_KEY=GENERA_UNA_CLAVE_NUEVA_AQUI

# Email para códigos de verificación
GMAIL_USER=camiloeagiraldodev@gmail.com
GMAIL_APP_PASSWORD=jpyy ympl thzq gfjc

# Google OAuth (si lo usas)
GOOGLE_CLIENT_ID=tu-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=tu-client-secret

# Binance API (opcional)
BINANCE_API_KEY=tu-api-key
BINANCE_API_SECRET=tu-api-secret
```

**Para generar nuevo SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Guarda con `Ctrl+O`, Enter, `Ctrl+X`

### 5.3 Crear Usuario Administrador

```bash
# Activar entorno virtual
source venv/bin/activate

# Crear admin
python3 create_admin.py

# Desactivar entorno
deactivate
```

---

## Paso 6: Configurar Nginx

### 6.1 Crear Configuración de Nginx

```bash
sudo nano /etc/nginx/sites-available/visual-strategy-creator
```

**Pega esta configuración:**

```nginx
server {
    listen 80;
    server_name tu-dominio.com www.tu-dominio.com;
    # O usa la IP del VPS si no tienes dominio aún
    # server_name 123.45.67.89;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    location /static {
        alias /var/www/visual-strategy-creator/static;
        expires 30d;
    }
}
```

### 6.2 Activar Sitio

```bash
# Crear enlace simbólico
sudo ln -s /etc/nginx/sites-available/visual-strategy-creator /etc/nginx/sites-enabled/

# Eliminar configuración default (opcional)
sudo rm /etc/nginx/sites-enabled/default

# Verificar configuración
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
```

---

## Paso 7: Configurar Supervisor (Mantener App Activa)

### 7.1 Crear Configuración de Supervisor

```bash
sudo nano /etc/supervisor/conf.d/visual-strategy-creator.conf
```

**Pega esta configuración:**

```ini
[program:visual-strategy-creator]
directory=/var/www/visual-strategy-creator
command=/var/www/visual-strategy-creator/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:5000 app:app
user=www-data
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/visual-strategy-creator/error.log
stdout_logfile=/var/log/visual-strategy-creator/access.log
environment=PATH="/var/www/visual-strategy-creator/venv/bin"
```

### 7.2 Crear Directorio de Logs

```bash
sudo mkdir -p /var/log/visual-strategy-creator
sudo chown www-data:www-data /var/log/visual-strategy-creator
```

### 7.3 Iniciar Supervisor

```bash
# Recargar configuración
sudo supervisorctl reread
sudo supervisorctl update

# Iniciar aplicación
sudo supervisorctl start visual-strategy-creator

# Verificar estado
sudo supervisorctl status
```

---

## Paso 8: Configurar HTTPS con Let's Encrypt (RECOMENDADO)

### 8.1 Instalar Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 8.2 Obtener Certificado SSL

```bash
# Reemplaza con tu dominio
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com
```

Certbot configurará automáticamente Nginx para HTTPS.

---

## Paso 9: Verificar Instalación

### 9.1 Probar Aplicación

Abre tu navegador en:
- **HTTP:** http://tu-dominio.com o http://tu-ip-vps
- **HTTPS:** https://tu-dominio.com (si configuraste SSL)

### 9.2 Login Admin

- **Email:** admin@tradingbot.com
- **Contraseña:** Admin2026! (cámbiala después del primer login)

---

## 📋 Comandos Útiles para Mantenimiento

### Ver Logs

```bash
# Logs de la aplicación
sudo tail -f /var/log/visual-strategy-creator/error.log
sudo tail -f /var/log/visual-strategy-creator/access.log

# Logs de Nginx
sudo tail -f /var/nginx/error.log
sudo tail -f /var/nginx/access.log
```

### Reiniciar Servicios

```bash
# Reiniciar aplicación
sudo supervisorctl restart visual-strategy-creator

# Reiniciar Nginx
sudo systemctl restart nginx

# Ver estado
sudo supervisorctl status
```

### Actualizar Código desde Git

```bash
# Ir al directorio
cd /var/www/visual-strategy-creator

# Descargar últimos cambios
git pull origin main

# Activar entorno virtual
source venv/bin/activate

# Actualizar dependencias si cambiaron
pip install -r requirements.txt

# Desactivar entorno
deactivate

# Reiniciar aplicación
sudo supervisorctl restart visual-strategy-creator
```

---

## 🔧 Troubleshooting

### Error: Aplicación no inicia

```bash
# Ver logs detallados
sudo supervisorctl tail -f visual-strategy-creator stderr

# Verificar permisos
sudo chown -R www-data:www-data /var/www/visual-strategy-creator
```

### Error: Nginx no se conecta

```bash
# Verificar que Gunicorn esté escuchando
sudo netstat -tlnp | grep 5000

# Verificar configuración de Nginx
sudo nginx -t
```

### Error: No llegan emails

```bash
# Verificar puerto SMTP
telnet smtp.gmail.com 587

# Si no funciona, verificar firewall
sudo ufw allow 587/tcp
```

---

## 🔐 Seguridad Adicional

### Configurar Firewall

```bash
# Permitir SSH, HTTP y HTTPS
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status
```

### Cambiar Contraseña del Admin

1. Login en la aplicación
2. Ve al Panel de Admin
3. Cambia la contraseña por una segura

---

## 📝 Resumen del Flujo de Trabajo

### Desarrollo en Local:
1. Modificas código
2. `git add .`
3. `git commit -m "descripción"`
4. `git push origin main`

### Actualizar en VPS:
1. SSH al VPS: `ssh usuario@ip`
2. `cd /var/www/visual-strategy-creator`
3. `git pull origin main`
4. `sudo supervisorctl restart visual-strategy-creator`

---

## ✅ Checklist Final

- [X] Repositorio Git creado en GitHub/GitLab
- [X] Código subido con `git push`
- [X] SSH configurado en VPS
- [X] Proyecto clonado en `/var/www/visual-strategy-creator`
- [X] `.env` configurado con SECRET_KEY nuevo
- [ ] Usuario admin creado
- [X] Nginx configurado y funcionando
- [X] Supervisor configurado
- [ ] SSL/HTTPS configurado (opcional pero recomendado)
- [ ] Firewall configurado
- [X] Aplicación accesible desde navegador
- [ ] Contraseña admin cambiada

---

**🎉 ¡Tu aplicación está lista en producción!**

**Acceso:** https://tu-dominio.com o http://tu-ip-vps

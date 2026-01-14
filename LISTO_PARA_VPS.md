# ✅ PROYECTO LISTO PARA VPS

## 📁 Archivos Preparados

Se han eliminado todos los archivos innecesarios para producción:

### ❌ Eliminados:
- Scripts de prueba (test_*.py, check_admin.py)
- Archivos batch de Windows (.bat)
- Documentación de desarrollo (MODO_DESARROLLO.md)
- Carpeta de respaldo (TradingBot_Original/)
- Cache de Python (__pycache__)

### ✅ Conservados (Listos para VPS):

**Archivos Python:**
- app.py (aplicación principal)
- database.py (base de datos)
- auth_routes.py (rutas de autenticación)
- admin_routes.py (panel admin)
- payments_routes.py (pagos)
- email_service.py (correo electrónico)
- google_auth.py (OAuth Google)
- create_admin.py (crear admin si es necesario)

**Configuración:**
- .env (configuración del servidor)
- .env.example (plantilla)
- .gitignore (archivos a ignorar)
- requirements.txt (dependencias Python)

**Scripts Linux:**
- install.sh (instalación automática)
- start.sh (iniciar en producción)
- start_dev.sh (modo desarrollo)
- verify_project.sh (verificar instalación)

**Templates:**
- Todos los archivos HTML en templates/

**Base de Datos:**
- database/tradingbot.db (con usuario admin creado)

**Documentación:**
- README.md (guía principal)
- DEPLOYMENT.md (guía de despliegue)
- LEEME.txt (resumen español)

---

## 👤 Usuario Administrador

✅ **Ya creado en la base de datos:**
- Email: admin@tradingbot.com
- Contraseña: Admin2026!
- Rol: admin
- Verificado: Sí

---

## 🚀 Próximos Pasos - Subir al VPS

### 1. Comprimir la carpeta (excluyendo venv):

**Opción A - ZIP Manual:**
1. Selecciona todos los archivos EXCEPTO `venv`
2. Clic derecho → Enviar a → Carpeta comprimida
3. Nombra: `visual-strategy-creator.zip`

**Opción B - PowerShell:**
```powershell
cd "C:\Users\Olga\Downloads\TradingBot"
Compress-Archive -Path "Visual strategy creator\*" -DestinationPath "visual-strategy-creator.zip" -Exclude "venv"
```

### 2. Subir al VPS:

```bash
# Conectar al VPS
ssh usuario@tu-vps-ip

# Crear directorio
mkdir -p /var/www/visual-strategy-creator

# Desde tu PC, subir archivo
scp visual-strategy-creator.zip usuario@tu-vps-ip:/var/www/
```

### 3. En el VPS, instalar:

```bash
# Descomprimir
cd /var/www
unzip visual-strategy-creator.zip -d visual-strategy-creator

# Dar permisos de ejecución a los scripts
cd visual-strategy-creator
chmod +x *.sh

# Ejecutar instalación automática
./install.sh
```

### 4. Configurar .env en el VPS:

```bash
nano .env
```

Asegúrate de que tenga:
```env
SECRET_KEY=2bcea8ee08dda3cd1d9c0ca0e15f2b431961434aca8bdc1c6d0fb4647264d57f
GMAIL_USER=camiloeagiraldodev@gmail.com
GMAIL_APP_PASSWORD=jpyy ympl thzq gfjc
```

### 5. Iniciar la aplicación:

```bash
# Modo producción con Gunicorn
./start.sh
```

---

## 📧 Registro de Usuarios en VPS

Una vez en el VPS, el envío de emails funcionará automáticamente:
- Los usuarios recibirán códigos por email
- No necesitas ver la consola para copiar códigos
- El sistema SMTP de Gmail funcionará sin bloqueos

---

## 🔒 Seguridad

Antes de hacer público:
1. Cambia el `SECRET_KEY` en `.env`
2. Configura HTTPS con Certbot/Let's Encrypt
3. Actualiza la contraseña del admin

---

## 📝 Notas Importantes

- ✅ NO subas la carpeta `venv` al VPS
- ✅ El VPS creará su propio entorno virtual
- ✅ La base de datos ya tiene el usuario admin
- ✅ Los emails funcionarán en el VPS (puerto 587 abierto)
- ✅ Todos los scripts `.sh` están listos para Linux

---

**¿Todo listo para comprimir y subir al VPS?**

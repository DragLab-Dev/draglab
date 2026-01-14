# 🔄 CÓMO ACTUALIZAR CÓDIGO EN EL VPS

## ⚡ PROCESO RÁPIDO (3 pasos)

### 1️⃣ En tu PC (Windows)

```powershell
# Ve a la carpeta del proyecto
cd "C:\Users\Olga\Downloads\TradingBot\Visual strategy creator"

# Agregar cambios
git add .

# Crear commit con descripción
git commit -m "Descripción de lo que cambiaste"

# Subir a GitHub/GitLab
git push origin main
```

**Ejemplo:**
```powershell
git add .
git commit -m "Agregué nuevo indicador RSI al backtest"
git push origin main
```

---

### 2️⃣ En el VPS (Hostinger)

```bash
# Conectar al VPS
ssh root@tu-ip-hostinger

# Ir a la carpeta del proyecto
cd /var/www/visual-strategy-creator

# Descargar cambios
git pull origin main

# Si cambiaste requirements.txt (nuevas dependencias):
source venv/bin/activate
pip install -r requirements.txt
deactivate

# Reiniciar la aplicación
sudo supervisorctl restart visual-strategy-creator
```

---

### 3️⃣ Verificar

Abre tu navegador y verifica que los cambios estén activos:
```
https://tu-dominio.com
```

---

## 📋 COMANDO TODO-EN-UNO

### Para tu PC:
```powershell
git add . ; git commit -m "Cambios realizados" ; git push origin main
```

### Para el VPS:
```bash
cd /var/www/visual-strategy-creator && git pull origin main && sudo supervisorctl restart visual-strategy-creator
```

---

## 🔍 Verificar Estado

### Ver qué archivos cambiaron:
```powershell
# En tu PC
git status
```

### Ver últimos commits:
```powershell
git log --oneline -5
```

### Ver diferencias antes de hacer commit:
```powershell
git diff
```

---

## 🚨 CASOS ESPECIALES

### Si cambiaste la base de datos:

```bash
# En el VPS
cd /var/www/visual-strategy-creator
source venv/bin/activate
python3 update_schema.py  # Si tienes script de migración
deactivate
sudo supervisorctl restart visual-strategy-creator
```

### Si cambiaste .env:

```bash
# En el VPS - NO se actualiza automáticamente porque está en .gitignore
nano .env
# Edita manualmente los valores
# Guarda: Ctrl+O, Enter, Ctrl+X

sudo supervisorctl restart visual-strategy-creator
```

### Si cambiaste templates HTML o CSS:

```bash
# Puede requerir limpiar caché del navegador
# En el navegador: Ctrl + Shift + R (Windows)
# O abrir en modo incógnito
```

---

## ❌ ERRORES COMUNES

### Error: "Your local changes would be overwritten"

```bash
# En el VPS
git stash  # Guarda cambios locales temporalmente
git pull origin main
git stash pop  # Restaura cambios (si los necesitas)
```

### Error: "Permission denied"

```bash
# Cambiar permisos
sudo chown -R $USER:$USER /var/www/visual-strategy-creator
```

### Error: La app no reinicia

```bash
# Ver logs de errores
sudo supervisorctl tail -f visual-strategy-creator stderr

# Ver todos los logs
sudo tail -f /var/log/visual-strategy-creator/error.log
```

---

## 📊 WORKFLOW COMPLETO

```
TU PC                          GITHUB                         VPS
------                         ------                         -----

1. Editas código
                git push ───────>  Repositorio
                                                    git pull <─── 2. Descargar
                                                                 3. Reiniciar app
                                                                 4. Cambios VIVOS
```

---

## 💡 TIPS PROFESIONALES

### 1. Commits frecuentes con mensajes claros:
```powershell
✅ BIEN: git commit -m "Fix: Corregido error en cálculo de EMA"
❌ MAL:  git commit -m "cambios"
```

### 2. Antes de hacer push, verifica:
```powershell
git status  # Ver qué cambió
git diff    # Ver diferencias específicas
```

### 3. Usar branches para features grandes:
```powershell
# Crear nueva rama para feature
git checkout -b nueva-funcionalidad

# Trabajar en la rama...
git add .
git commit -m "Nueva funcionalidad"
git push origin nueva-funcionalidad

# En GitHub: Crear Pull Request
# Después de aprobar: Merge to main

# En VPS, hacer pull de main actualizado
```

---

## 🎯 RESUMEN ULTRA-RÁPIDO

### Cambios simples (CSS, texto, pequeñas correcciones):

**PC:**
```powershell
git add . && git commit -m "Fix CSS" && git push
```

**VPS:**
```bash
cd /var/www/visual-strategy-creator && git pull && sudo supervisorctl restart visual-strategy-creator
```

**Tiempo total: ~1 minuto** ⚡

---

## 🔄 AUTOMATIZACIÓN (Avanzado)

### Crear script de actualización en VPS:

```bash
# Crear script
nano ~/update-app.sh
```

**Contenido:**
```bash
#!/bin/bash
cd /var/www/visual-strategy-creator
echo "📥 Descargando cambios..."
git pull origin main
echo "🔄 Reiniciando aplicación..."
sudo supervisorctl restart visual-strategy-creator
echo "✅ Aplicación actualizada!"
```

**Dar permisos y usar:**
```bash
chmod +x ~/update-app.sh

# Cada vez que quieras actualizar:
~/update-app.sh
```

---

## 📞 ¿NECESITAS AYUDA?

### Ver logs en tiempo real:
```bash
sudo supervisorctl tail -f visual-strategy-creator
```

### Estado de la aplicación:
```bash
sudo supervisorctl status
```

### Reinicio completo:
```bash
sudo supervisorctl restart all
sudo systemctl restart nginx
```

---

**¿Algún problema? Revisa la sección de Troubleshooting en DEPLOYMENT_HOSTINGER_GIT.md**

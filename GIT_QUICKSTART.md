# 🚀 GUÍA RÁPIDA: GIT → HOSTINGER VPS

## 📋 Resumen del Proceso (5 Pasos)

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   TU PC         │ ───> │  GITHUB/GITLAB  │ ───> │  HOSTINGER VPS  │
│  (Windows)      │ git  │  (Repositorio)  │ git  │    (Linux)      │
└─────────────────┘ push └─────────────────┘ pull └─────────────────┘
```

---

## ⚡ Inicio Rápido

### 1️⃣ En tu PC (Windows) - 2 minutos

```powershell
# Opción A: Script automático
git_init.bat

# Opción B: Manual
git init
git add .
git commit -m "Initial commit"
```

### 2️⃣ Crear Repo en GitHub - 1 minuto

1. https://github.com/new
2. Nombre: `visual-strategy-creator`
3. Privado ✅
4. Click "Create"

### 3️⃣ Conectar y Subir - 1 minuto

```powershell
git remote add origin https://github.com/TU_USUARIO/visual-strategy-creator.git
git branch -M main
git push -u origin main
```

### 4️⃣ En el VPS (SSH) - 5 minutos

```bash
# Conectar
ssh root@tu-ip-hostinger

# Instalar dependencias
sudo apt update && sudo apt install -y python3 python3-pip python3-venv git nginx supervisor

# Clonar proyecto
cd /var/www
git clone https://github.com/TU_USUARIO/visual-strategy-creator.git
cd visual-strategy-creator

# Instalar
chmod +x *.sh
./install.sh

# Configurar .env
nano .env  # Actualiza SECRET_KEY y emails
```

### 5️⃣ Configurar Nginx y Supervisor - 3 minutos

```bash
# Ver guía completa en: DEPLOYMENT_HOSTINGER_GIT.md
# Paso 6 y Paso 7
```

---

## 🔄 Actualizar Código (Workflow Diario)

### En tu PC:
```powershell
# Hiciste cambios en el código
git add .
git commit -m "Descripción de cambios"
git push origin main
```

### En el VPS:
```bash
cd /var/www/visual-strategy-creator
git pull origin main
sudo supervisorctl restart visual-strategy-creator
```

---

## 📁 Archivos Importantes

| Archivo | Propósito |
|---------|-----------|
| `DEPLOYMENT_HOSTINGER_GIT.md` | Guía completa paso a paso |
| `git_init.bat` | Script para inicializar Git en Windows |
| `.gitignore` | Archivos que NO se suben a Git |
| `.env.example` | Plantilla de configuración |
| `install.sh` | Instalación automática en VPS |

---

## ⚠️ IMPORTANTE: No Subir a Git

El `.gitignore` ya está configurado para excluir:

- ✅ `.env` (contraseñas y secrets)
- ✅ `venv/` (entorno virtual)
- ✅ `database/*.db` (base de datos con usuarios)
- ✅ `__pycache__/` (caché de Python)

**Solo se sube el código fuente y configuración de ejemplo.**

---

## 🔐 Seguridad

### En el `.env` del VPS:

1. **Genera nuevo SECRET_KEY:**
   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Configura tus credenciales:**
   - Gmail para emails
   - Google OAuth (opcional)
   - Binance API (opcional)

3. **Nunca** compartas el `.env` en Git

---

## 📞 Ayuda

- **Guía Completa:** [DEPLOYMENT_HOSTINGER_GIT.md](DEPLOYMENT_HOSTINGER_GIT.md)
- **Problemas comunes:** Ver sección Troubleshooting en la guía completa
- **Logs en VPS:**
  ```bash
  sudo tail -f /var/log/visual-strategy-creator/error.log
  ```

---

## ✅ Checklist Rápido

**En tu PC:**
- [ ] Git instalado
- [ ] Repositorio inicializado (`git init`)
- [ ] Código subido a GitHub/GitLab (`git push`)

**En Hostinger VPS:**
- [ ] SSH funciona
- [ ] Git instalado
- [ ] Proyecto clonado
- [ ] `.env` configurado
- [ ] Nginx funcionando
- [ ] Aplicación accesible en navegador

---

**¿Todo listo? Ejecuta `git_init.bat` y sigue la guía completa.**

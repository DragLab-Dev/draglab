#!/bin/bash
# ==================================================
# VERIFICACIÓN DE PROYECTO - Visual Strategy Creator
# ==================================================
# Este script verifica que todos los archivos necesarios estén presentes

echo "=================================================="
echo "🔍 Verificando proyecto Visual Strategy Creator"
echo "=================================================="
echo ""

# Contador de errores
ERRORS=0

# Función para verificar archivo
check_file() {
    if [ -f "$1" ]; then
        echo "✅ $1"
    else
        echo "❌ FALTA: $1"
        ((ERRORS++))
    fi
}

# Función para verificar directorio
check_dir() {
    if [ -d "$1" ]; then
        echo "✅ $1/"
    else
        echo "❌ FALTA: $1/"
        ((ERRORS++))
    fi
}

echo "📁 Archivos Python:"
check_file "app.py"
check_file "database.py"
check_file "auth_routes.py"
check_file "admin_routes.py"
check_file "payments_routes.py"
check_file "google_auth.py"
check_file "email_service.py"

echo ""
echo "📝 Archivos de Configuración:"
check_file ".env.example"
check_file ".gitignore"
check_file "requirements.txt"

echo ""
echo "📚 Documentación:"
check_file "README.md"
check_file "DEPLOYMENT.md"
check_file "GIT_GUIDE.md"
check_file "QUICKSTART.md"
check_file "INSTRUCCIONES_FINALES.md"

echo ""
echo "🔧 Scripts:"
check_file "install.sh"
check_file "install.bat"
check_file "start.sh"
check_file "start.bat"
check_file "start_dev.sh"

echo ""
echo "📂 Directorios:"
check_dir "templates"
check_dir "database"
check_dir "data"

echo ""
echo "🌐 Templates HTML:"
check_file "templates/index.html"
check_file "templates/login.html"
check_file "templates/register.html"
check_file "templates/welcome.html"
check_file "templates/backtest.html"
check_file "templates/admin_panel.html"
check_file "templates/user_panel.html"
check_file "templates/subscriptions.html"

echo ""
echo "=================================================="
if [ $ERRORS -eq 0 ]; then
    echo "✅ VERIFICACIÓN COMPLETA: Proyecto listo para Git"
    echo "=================================================="
    echo ""
    echo "Próximos pasos:"
    echo "1. git init"
    echo "2. git add ."
    echo "3. git commit -m 'Initial commit: Visual Strategy Creator v2.4'"
    echo "4. Crear repositorio en GitHub/GitLab (Private)"
    echo "5. git remote add origin TU-URL"
    echo "6. git push -u origin main"
else
    echo "❌ ERRORES ENCONTRADOS: $ERRORS archivos faltantes"
    echo "=================================================="
    exit 1
fi

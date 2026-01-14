#!/bin/bash
# ==================================================
# VISUAL STRATEGY CREATOR - SCRIPT DE INSTALACIÓN
# ==================================================
# Para configuración inicial en VPS Linux

echo "=================================================="
echo "📦 Instalador Visual Strategy Creator"
echo "=================================================="

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado"
    echo "   Instala Python 3.8+ antes de continuar"
    exit 1
fi

echo "✅ Python $(python3 --version) detectado"

# Crear entorno virtual
echo "📦 Creando entorno virtual..."
python3 -m venv venv
source venv/bin/activate

# Actualizar pip
echo "📦 Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip install -r requirements.txt

# Configurar .env
if [ ! -f ".env" ]; then
    echo "📝 Creando archivo .env..."
    cp .env.example .env
    echo "⚠️  IMPORTANTE: Edita .env con tus credenciales"
    echo "   nano .env"
else
    echo "✅ Archivo .env ya existe"
fi

# Crear directorios necesarios
echo "📁 Creando directorios..."
mkdir -p database
mkdir -p data

# Dar permisos de ejecución
echo "🔧 Configurando permisos..."
chmod +x start.sh
chmod +x start_dev.sh

echo "=================================================="
echo "✅ Instalación completada"
echo "=================================================="
echo ""
echo "Próximos pasos:"
echo "1. Edita .env con tus credenciales:"
echo "   nano .env"
echo ""
echo "2. Inicia la aplicación:"
echo "   ./start.sh        # Modo producción con Gunicorn"
echo "   ./start_dev.sh    # Modo desarrollo con Flask"
echo ""
echo "=================================================="

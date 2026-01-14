#!/bin/bash
# ==================================================
# VISUAL STRATEGY CREATOR - MODO DESARROLLO
# ==================================================
# Para desarrollo local con Flask debug

echo "=================================================="
echo "🔧 Iniciando Visual Strategy Creator (Desarrollo)"
echo "=================================================="

# Activar entorno virtual
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Error: No se encontró el entorno virtual"
    echo "   Ejecuta: python3 -m venv venv"
    exit 1
fi

# Verificar .env
if [ ! -f ".env" ]; then
    echo "⚠️  Advertencia: No se encontró .env"
    echo "   Creando desde .env.example..."
    cp .env.example .env
fi

# Variables de entorno para desarrollo
export FLASK_ENV=development
export FLASK_DEBUG=True

# Iniciar con Flask development server
echo "✅ Iniciando servidor de desarrollo..."
echo "   Modo: Desarrollo"
echo "   Debug: Activado"
echo "   Puerto: 5000"
echo "=================================================="

python app.py

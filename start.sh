#!/bin/bash
# ==================================================
# VISUAL STRATEGY CREATOR - SCRIPT DE INICIO
# ==================================================
# Para Linux/Mac VPS

echo "=================================================="
echo "🚀 Iniciando Visual Strategy Creator"
echo "=================================================="

# Activar entorno virtual
if [ -d "venv" ]; then
    echo "✅ Activando entorno virtual..."
    source venv/bin/activate
else
    echo "❌ Error: No se encontró el entorno virtual"
    echo "   Ejecuta: python3 -m venv venv"
    exit 1
fi

# Verificar archivo .env
if [ ! -f ".env" ]; then
    echo "❌ Error: No se encontró archivo .env"
    echo "   Copia .env.example a .env y configura las variables"
    exit 1
fi

# Verificar dependencias
echo "✅ Verificando dependencias..."
pip install -q -r requirements.txt

# Crear directorio de base de datos si no existe
mkdir -p database

# Iniciar aplicación con Gunicorn (producción)
echo "✅ Iniciando servidor con Gunicorn..."
echo "   Modo: Producción"
echo "   Workers: 3"
echo "   Puerto: 5000"
echo "=================================================="

gunicorn --workers 3 --bind 0.0.0.0:5000 --timeout 120 --access-logfile - --error-logfile - app:app

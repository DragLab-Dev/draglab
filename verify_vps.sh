#!/bin/bash
# Script para verificar la instalación en el VPS

echo "🔍 Verificando archivos en VPS..."

cd /var/www/visual-strategy-creator

echo ""
echo "📁 Estructura de directorios:"
ls -la

echo ""
echo "📂 Contenido de static/:"
ls -la static/

echo ""
echo "📂 Contenido de static/css/:"
ls -la static/css/

echo ""
echo "📂 Contenido de static/js/:"
ls -la static/js/

echo ""
echo "📄 Verificando archivos del menú universal:"
if [ -f "static/css/universal_menu.css" ]; then
    echo "✅ static/css/universal_menu.css existe"
    wc -l static/css/universal_menu.css
else
    echo "❌ static/css/universal_menu.css NO EXISTE"
fi

if [ -f "static/js/universal_menu.js" ]; then
    echo "✅ static/js/universal_menu.js existe"
    wc -l static/js/universal_menu.js
else
    echo "❌ static/js/universal_menu.js NO EXISTE"
fi

echo ""
echo "🔄 Estado de Git:"
git status

echo ""
echo "📡 Branch actual:"
git branch

echo ""
echo "🔄 Haciendo git pull..."
git pull origin main

echo ""
echo "♻️ Reiniciando servicio..."
sudo supervisorctl restart visual-strategy-creator

echo ""
echo "📊 Estado del servicio:"
supervisorctl status visual-strategy-creator

echo ""
echo "✅ Verificación completa!"

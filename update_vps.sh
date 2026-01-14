#!/bin/bash

# ==================================================
# SCRIPT DE ACTUALIZACIÓN AUTOMÁTICA
# Para VPS Hostinger
# ==================================================

echo "============================================"
echo "  ACTUALIZANDO APLICACIÓN"
echo "============================================"
echo ""

# Ir al directorio del proyecto
cd /var/www/visual-strategy-creator || exit 1

echo "📥 Descargando últimos cambios desde GitHub..."
git pull origin main

if [ $? -ne 0 ]; then
    echo "❌ Error al descargar cambios"
    exit 1
fi

echo ""
echo "✅ Cambios descargados correctamente"
echo ""

# Verificar si requirements.txt cambió
if git diff HEAD@{1} HEAD --name-only | grep -q "requirements.txt"; then
    echo "📦 Detectado cambio en requirements.txt"
    echo "   Actualizando dependencias..."
    source venv/bin/activate
    pip install -r requirements.txt
    deactivate
    echo "✅ Dependencias actualizadas"
fi

echo ""
echo "🔄 Reiniciando aplicación..."
sudo supervisorctl restart visual-strategy-creator

if [ $? -ne 0 ]; then
    echo "❌ Error al reiniciar la aplicación"
    exit 1
fi

echo ""
echo "⏳ Esperando a que la aplicación inicie..."
sleep 3

# Verificar estado
STATUS=$(sudo supervisorctl status visual-strategy-creator | grep RUNNING)

if [ -z "$STATUS" ]; then
    echo "❌ La aplicación no está corriendo"
    echo ""
    echo "Ver logs con:"
    echo "  sudo supervisorctl tail -f visual-strategy-creator stderr"
    exit 1
fi

echo ""
echo "============================================"
echo "  ✅ APLICACIÓN ACTUALIZADA EXITOSAMENTE"
echo "============================================"
echo ""
echo "Estado: $STATUS"
echo ""
echo "📊 Ver logs en tiempo real:"
echo "   sudo tail -f /var/log/visual-strategy-creator/error.log"
echo ""

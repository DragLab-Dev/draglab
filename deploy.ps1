# Script para actualizar el VPS automáticamente

Write-Host "📤 Subiendo cambios a GitHub..." -ForegroundColor Cyan
git push origin main

Write-Host "`n🔄 Conectando con VPS para actualizar..." -ForegroundColor Cyan
Write-Host "⚠️  Ingresa la contraseña del VPS cuando se solicite" -ForegroundColor Yellow

ssh appuser@72.62.169.37 @"
cd /var/www/visual-strategy-creator
echo '📥 Descargando cambios...'
git pull origin main
echo '🔄 Reiniciando servicio...'
sudo supervisorctl restart visual-strategy-creator
echo '✅ Actualización completada!'
supervisorctl status visual-strategy-creator
"@

Write-Host "`n✅ Proceso completado!" -ForegroundColor Green
Write-Host "🌐 Accede a: http://72.62.169.37" -ForegroundColor Cyan

@echo off
cls
echo ============================================
echo   ACTUALIZAR CODIGO EN GITHUB
echo ============================================
echo.

REM Verificar si hay cambios
git status

echo.
echo ============================================
set /p mensaje="Describe tus cambios: "

if "%mensaje%"=="" (
    set mensaje=Actualizacion de codigo
)

echo.
echo Agregando archivos...
git add .

echo Creando commit...
git commit -m "%mensaje%"

echo Subiendo a GitHub...
git push origin main

echo.
echo ============================================
echo  CODIGO ACTUALIZADO EN GITHUB
echo ============================================
echo.
echo Siguiente paso:
echo   1. Conectate al VPS: ssh root@tu-ip
echo   2. Ejecuta: cd /var/www/visual-strategy-creator
echo   3. Ejecuta: git pull origin main
echo   4. Ejecuta: sudo supervisorctl restart visual-strategy-creator
echo.
echo O revisa: COMO_ACTUALIZAR.md
echo.
pause

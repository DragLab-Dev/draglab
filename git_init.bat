@echo off
echo ====================================
echo GIT - CONFIGURACION INICIAL
echo ====================================
echo.

REM Verificar si Git esta instalado
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Git no esta instalado.
    echo.
    echo Descarga Git desde: https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
)

echo [OK] Git esta instalado
echo.

REM Inicializar repositorio si no existe
if not exist ".git" (
    echo Inicializando repositorio Git...
    git init
    echo [OK] Repositorio inicializado
    echo.
) else (
    echo [OK] Repositorio Git ya existe
    echo.
)

REM Agregar todos los archivos
echo Agregando archivos al repositorio...
git add .
echo [OK] Archivos agregados
echo.

REM Crear commit
echo Creando commit inicial...
git commit -m "Initial commit - Visual Strategy Creator"
echo [OK] Commit creado
echo.

echo ====================================
echo SIGUIENTE PASO:
echo ====================================
echo.
echo 1. Crea un repositorio en GitHub o GitLab
echo 2. Ejecuta estos comandos:
echo.
echo    git remote add origin https://github.com/TU_USUARIO/visual-strategy-creator.git
echo    git branch -M main
echo    git push -u origin main
echo.
echo 3. Luego sigue la guia: DEPLOYMENT_HOSTINGER_GIT.md
echo.
pause

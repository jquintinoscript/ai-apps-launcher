@echo off
title AI Apps Launcher
color 0A

echo.
echo ========================================
echo   AI Apps Launcher - Instalacao
echo ========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo Baixe em: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python detectado
echo [INFO] Instalando dependencias...
pip install -r requirements.txt

echo.
echo [OK] Pronto! Iniciando...
echo.

python app.py
pause
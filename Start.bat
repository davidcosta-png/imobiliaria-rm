@echo off
setlocal
cd /d "%~dp0"
title Start Imobiliaria RM
color 0A
where py >nul 2>&1
if errorlevel 1 (
  where python >nul 2>&1
  if errorlevel 1 (
    echo Python nao encontrado
    pause
    exit /b 1
  )
)
if not exist "venv\Scripts\python.exe" (
  py -3 -m venv "venv" 2>nul || python -m venv "venv"
)
"venv\Scripts\python.exe" -m pip install --upgrade pip >nul 2>&1
set /p APP_USER="Login: "
set /p APP_PASS="Senha: "
echo ==========================================
echo  INICIO
echo ==========================================
echo 3 ^) Menu completo
set /p DUMMY="Escolha 3 para iniciar: "
"venv\Scripts\python.exe" -u "main.py"
pause

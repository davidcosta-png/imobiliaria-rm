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
set /p TIPO_IMOVEL="Tipo (apartamento/casa/estudio): "
set /p NUM_QUARTOS="Quartos (1-2, se aplicavel): "
set /p TEM_CRIANCAS="Possui criancas? (S/N, apartamento): "
set /p VAGA_GARAGEM="Vaga de garagem? (S/N, apt/casa): "
set /p NUM_VAGAS="Vagas estacionamento (estudio): "
set /p PARCELAS_CONTRATO="Parcelas contrato (1-5): "
set /p GERAR_CSV="Gerar CSV? (S/N): "
if /i "%GERAR_CSV%"=="S" (
  set /p CSV_NOME="Nome do arquivo CSV (opcional): "
)
set AUTO_START=1
set TIPO_IMOVEL=%TIPO_IMOVEL%
set NUM_QUARTOS=%NUM_QUARTOS%
set TEM_CRIANCAS=%TEM_CRIANCAS%
set VAGA_GARAGEM=%VAGA_GARAGEM%
set NUM_VAGAS=%NUM_VAGAS%
set PARCELAS_CONTRATO=%PARCELAS_CONTRATO%
set GERAR_CSV=%GERAR_CSV%
set CSV_NOME=%CSV_NOME%
"venv\Scripts\python.exe" -u "main.py"
pause

@echo off
REM Script de execução rápida - PostgreSQL Windows

echo 🚀 SISTEMA DE ATUALIZAÇÃO CTE - POSTGRESQL
echo =========================================

if "%1"=="" (
    echo 📄 Uso: %0 ^<arquivo_excel^>
    echo Exemplo: %0 atualizacoes.xlsx
    exit /b 1
)

set ARQUIVO=%1
set MODO=%2
if "%MODO%"=="" set MODO=empty_only
set BATCH=%3
if "%BATCH%"=="" set BATCH=100

if not exist "%ARQUIVO%" (
    echo ❌ Arquivo não encontrado: %ARQUIVO%
    exit /b 1
)

echo 📋 Configuração:
echo   - Arquivo: %ARQUIVO%
echo   - Modo: %MODO%
echo   - Lote: %BATCH%
echo.

echo 👁️ Preview das alterações:
python bulk_update_cte.py --update-file "%ARQUIVO%" --mode "%MODO%" --preview-only

echo.
set /p CONFIRMA="▶️ Executar atualizações? (s/N): "

if /i "%CONFIRMA%"=="s" (
    echo 🔄 Executando atualizações...
    python bulk_update_cte.py --update-file "%ARQUIVO%" --mode "%MODO%" --batch-size "%BATCH%"
) else (
    echo ❌ Execução cancelada
)

pause

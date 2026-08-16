@echo off
REM ============================================================================
REM Script de build automatizado para Sistema BPO Financeiro
REM Gera executável standalone (PyInstaller) e instalador Windows (Inno Setup)
REM ============================================================================

setlocal enabledelayedexpansion

REM Configurações
set PROJECT_ROOT=%~dp0
set BUILD_DIR=%PROJECT_ROOT%dist
set PYINSTALLER_SPEC=%PROJECT_ROOT%build.spec
set INNO_SCRIPT=%PROJECT_ROOT%installer.iss
set VERSION=1.0.0

REM Cores para output
set GREEN=\033[92m
set RED=\033[91m
set YELLOW=\033[93m
set BLUE=\033[94m
set RESET=\033[0m

echo ============================================================================
echo  BUILD DO SISTEMA BPO FINANCEIRO - v%VERSION%
echo ============================================================================
echo.

REM ----------------------------------------------------------------------------
REM Verifica dependências
REM ----------------------------------------------------------------------------
echo [%BLUE%INFO%RESET%] Verificando dependências...

where pyinstaller >nul 2>nul
if %errorlevel% neq 0 (
    echo [%RED%ERRO%RESET%] PyInstaller não encontrado. Instale com: pip install pyinstaller
    exit /b 1
)

where iscc >nul 2>nul
if %errorlevel% neq 0 (
    echo [%RED%ERRO%RESET%] Inno Setup Compiler (iscc) não encontrado.
    echo    Instale o Inno Setup em: https://jrsoftware.org/isdl.php
    echo    E adicione o diretório de instalação ao PATH (ex: C:\Program Files (x86)\Inno Setup 6)
    exit /b 1
)

echo [%GREEN%OK%RESET%] Dependências encontradas
echo.

REM ----------------------------------------------------------------------------
REM Limpa builds anteriores
REM ----------------------------------------------------------------------------
echo [%BLUE%INFO%RESET%] Limpando builds anteriores...
if exist "%BUILD_DIR%" (
    rmdir /s /q "%BUILD_DIR%" 2>nul
)
if exist "%PROJECT_ROOT%build" (
    rmdir /s /q "%PROJECT_ROOT%build" 2>nul
)
if exist "%PROJECT_ROOT%__pycache__" (
    rmdir /s /q "%PROJECT_ROOT%__pycache__" 2>nul
)
echo [%GREEN%OK%RESET%] Limpeza concluída
echo.

REM ----------------------------------------------------------------------------
REM Build com PyInstaller
REM ----------------------------------------------------------------------------
echo [%BLUE%INFO%RESET%] Compilando executável standalone com PyInstaller...
echo.

cd /d "%PROJECT_ROOT%"
pyinstaller --clean --noconfirm "%PYINSTALLER_SPEC%"

if %errorlevel% neq 0 (
    echo [%RED%ERRO%RESET%] Falha na compilação PyInstaller
    exit /b 1
)

echo.
echo [%GREEN%OK%RESET%] Executável criado em: %BUILD_DIR%\SistemaBPOFinanceiro
echo.

REM ----------------------------------------------------------------------------
REM Verifica se o executável foi criado
REM ----------------------------------------------------------------------------
set EXE_PATH=%BUILD_DIR%\SistemaBPOFinanceiro\SistemaBPOFinanceiro.exe
if not exist "%EXE_PATH%" (
    echo [%RED%ERRO%RESET%] Executável não encontrado em: %EXE_PATH%
    exit /b 1
)

echo [%BLUE%INFO%RESET%] Executável verificado: %EXE_PATH%
echo.

REM ----------------------------------------------------------------------------
REM Compila instalador com Inno Setup
REM ----------------------------------------------------------------------------
echo [%BLUE%INFO%RESET%] Compilando instalador Windows com Inno Setup...
echo.

cd /d "%PROJECT_ROOT%"
iscc "%INNO_SCRIPT%"

if %errorlevel% neq 0 (
    echo [%RED%ERRO%RESET%] Falha na compilação Inno Setup
    exit /b 1
)

echo.
echo [%GREEN%OK%RESET%] Instalador criado com sucesso!
echo.

REM ----------------------------------------------------------------------------
REM Lista arquivos gerados
REM ----------------------------------------------------------------------------
echo ============================================================================
echo  ARQUIVOS GERADOS
echo ============================================================================
dir "%BUILD_DIR%\installer\*.exe" /b /o:- 2>nul
echo.

REM ----------------------------------------------------------------------------
REM Informações de mitigação SmartScreen/Antivírus
REM ----------------------------------------------------------------------------
echo ============================================================================
echo  NOTAS IMPORTANTES - MITIGAÇÃO SMARTSCREEN / ANTIVÍRUS
echo ============================================================================
echo.
echo [%YELLOW%AVISO%RESET%] Para evitar bloqueios do Windows SmartScreen e antivírus:
echo.
echo   1. ASSINATURA DIGITAL (RECOMENDADO):
echo      - Obtenha um certificado Code Signing (EV preferred) de uma CA confiável
echo      - Configure SignTool no script .iss ou assine manualmente:
echo        signtool sign /a /v /tr http://timestamp.digicert.com /td sha256 /fd sha256 "dist\installer\SistemaBPOFinanceiro_Setup_1.0.0.exe"
echo.
echo   2. REPUTAÇÃO DO ARQUIVO:
echo      - Distribua o instalador por canais oficiais (site HTTPS, Microsoft Store)
echo      - Evite hospedar em compartilhamentos de arquivo suspeitos
echo      - Submeta para análise no VirusTotal após build: https://www.virustotal.com
echo.
echo   3. COMPORTAMENTO DO INSTALADOR:
echo      - Instalador solicita admin (necessário para Program Files)
echo      - Não faz download de componentes externos
echo      - Não modifica registro do sistema além do necessário
echo      - Não instala drivers ou serviços
echo.
echo   4. TESTE EM AMBIENTE LIMPO:
echo      - Teste em VM Windows limpo antes de distribuir
echo      - Verifique com Windows Defender e principais AVs
echo.

echo ============================================================================
echo  BUILD CONCLUÍDO COM SUCESSO!
echo ============================================================================
echo.
echo Instalador: %BUILD_DIR%\installer\SistemaBPOFinanceiro_Setup_%VERSION%.exe
echo.

pause
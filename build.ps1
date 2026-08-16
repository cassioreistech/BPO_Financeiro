<# 
.SYNOPSIS
    Build script para Sistema BPO Financeiro - PowerShell version
.DESCRIPTION
    Gera executável standalone (PyInstaller) e instalador Windows (Inno Setup)
    com mitigações para SmartScreen e antivírus.
#>

param(
    [string]$Version = "1.0.0",
    [switch]$CleanOnly,
    [switch]$SkipPyInstaller,
    [switch]$SkipInnoSetup,
    [switch]$SignInstaller,
    [string]$CertThumbprint,
    [string]$TimestampUrl = "http://timestamp.digicert.com"
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$BuildDir = Join-Path $ProjectRoot "dist"
$PyInstallerSpec = Join-Path $ProjectRoot "build.spec"
$InnoScript = Join-Path $ProjectRoot "installer.iss"

function Write-Color($Message, $Color = "White") {
    Write-Host $Message -ForegroundColor $Color
}

function Check-Command($Command, $Name, $InstallHint) {
    $path = (Get-Command $Command -ErrorAction SilentlyContinue).Source
    if (-not $path) {
        Write-Color "[ERRO] $Name não encontrado." -Color Red
        Write-Color "  $InstallHint" -Color Yellow
        exit 1
    }
    Write-Color "[OK] $Name encontrado: $path" -Color Green
}

Write-Color "============================================================================" -Color Cyan
Write-Color "  BUILD DO SISTEMA BPO FINANCEIRO - v$Version" -Color Cyan
Write-Color "============================================================================" -Color Cyan
Write-Host ""

# Verifica dependências
Write-Color "[INFO] Verificando dependências..." -Color Blue
Check-Command "pyinstaller" "PyInstaller" "Instale com: pip install pyinstaller"
Check-Command "iscc" "Inno Setup Compiler (iscc)" "Instale em: https://jrsoftware.org/isdl.php e adicione ao PATH"

if ($CleanOnly) {
    Write-Color "[INFO] Limpando builds anteriores..." -Color Blue
    $pathsToClean = @($BuildDir, (Join-Path $ProjectRoot "build"), (Join-Path $ProjectRoot "__pycache__"))
    $pathsToClean | ForEach-Object {
        if (Test-Path $_) { Remove-Item $_ -Recurse -Force -ErrorAction SilentlyContinue }
    }
    Write-Color "[OK] Limpeza concluída" -Color Green
    exit 0
}

# Limpa builds anteriores
Write-Color "[INFO] Limpando builds anteriores..." -Color Blue
$pathsToClean = @($BuildDir, (Join-Path $ProjectRoot "build"), (Join-Path $ProjectRoot "__pycache__"))
$pathsToClean | ForEach-Object {
    if (Test-Path $_) { Remove-Item $_ -Recurse -Force -ErrorAction SilentlyContinue }
}
Write-Color "[OK] Limpeza concluída" -Color Green

# Build PyInstaller
if (-not $SkipPyInstaller) {
    Write-Color "[INFO] Compilando executável standalone com PyInstaller..." -Color Blue
    Write-Host ""
    
    Set-Location $ProjectRoot
    & pyinstaller --clean --noconfirm $PyInstallerSpec
    
    if ($LASTEXITCODE -ne 0) {
        Write-Color "[ERRO] Falha na compilação PyInstaller" -Color Red
        exit 1
    }
    Write-Color "[OK] Executável criado em: $BuildDir\SistemaBPOFinanceiro" -Color Green
    Write-Host ""
}

# Verifica executável
$ExePath = Join-Path $BuildDir "SistemaBPOFinanceiro\SistemaBPOFinanceiro.exe"
if (-not (Test-Path $ExePath)) {
    Write-Color "[ERRO] Executável não encontrado: $ExePath" -Color Red
    exit 1
}
Write-Color "[INFO] Executável verificado: $ExePath" -Color Blue

# Build Inno Setup
if (-not $SkipInnoSetup) {
    Write-Color "[INFO] Compilando instalador Windows com Inno Setup..." -Color Blue
    Write-Host ""
    
    Set-Location $ProjectRoot
    & iscc $InnoScript
    
    if ($LASTEXITCODE -ne 0) {
        Write-Color "[ERRO] Falha na compilação Inno Setup" -Color Red
        exit 1
    }
    Write-Color "[OK] Instalador criado com sucesso!" -Color Green
    Write-Host ""
}

# Assina instalador (opcional)
if ($SignInstaller) {
    if (-not $CertThumbprint) {
        Write-Color "[ERRO] CertThumbprint obrigatório para assinatura" -Color Red
        exit 1
    }
    
    $InstallerPath = Get-ChildItem (Join-Path $BuildDir "installer\*.exe") | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($InstallerPath) {
        Write-Color "[INFO] Assinando instalador digitalmente..." -Color Blue
        & signtool sign /sha1 $CertThumbprint /tr $TimestampUrl /td sha256 /fd sha256 /v $InstallerPath.FullName
        if ($LASTEXITCODE -eq 0) {
            Write-Color "[OK] Instalador assinado com sucesso" -Color Green
        } else {
            Write-Color "[ERRO] Falha na assinatura digital" -Color Red
            exit 1
        }
    }
}

# Lista arquivos gerados
Write-Color "============================================================================" -Color Cyan
Write-Color "  ARQUIVOS GERADOS" -Color Cyan
Write-Color "============================================================================" -Color Cyan
Get-ChildItem (Join-Path $BuildDir "installer\*.exe") -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Color "  $($_.Name) - $([math]::Round($_.Length/1MB, 2)) MB" -Color White
}
Write-Host ""

# Notas de mitigação
Write-Color "============================================================================" -Color Cyan
Write-Color "  NOTAS IMPORTANTES - MITIGAÇÃO SMARTSCREEN / ANTIVÍRUS" -Color Cyan
Write-Color "============================================================================" -Color Cyan
Write-Host ""
Write-Color "1. ASSINATURA DIGITAL (RECOMENDADO):" -Color Yellow
Write-Color "   - Obtenha certificado Code Signing (EV preferred) de CA confiável" -Color White
Write-Color "   - Use: .\build.ps1 -SignInstaller -CertThumbprint <THUMBPRINT>" -Color White
Write-Host ""
Write-Color "2. REPUTAÇÃO DO ARQUIVO:" -Color Yellow
Write-Color "   - Distribua por canais oficiais (site HTTPS, Microsoft Store)" -Color White
Write-Color "   - Submeta para análise no VirusTotal: https://www.virustotal.com" -Color White
Write-Host ""
Write-Color "3. COMPORTAMENTO DO INSTALADOR:" -Color Yellow
Write-Color "   - Solicita admin apenas para Program Files" -Color White
Write-Color "   - Sem downloads externos, drivers ou serviços" -Color White
Write-Color "   - Modifica registro apenas para desinstalação" -Color White
Write-Host ""
Write-Color "4. TESTE EM AMBIENTE LIMPO:" -Color Yellow
Write-Color "   - Teste em VM Windows limpo antes de distribuir" -Color White
Write-Color "   - Verifique com Windows Defender e principais AVs" -Color White
Write-Host ""

Write-Color "============================================================================" -Color Cyan
Write-Color "  BUILD CONCLUÍDO COM SUCESSO!" -Color Green
Write-Color "============================================================================" -Color Cyan
Write-Host ""
$InstallerFinal = Get-ChildItem (Join-Path $BuildDir "installer\*.exe") | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if ($InstallerFinal) {
    Write-Color "Instalador: $($InstallerFinal.FullName)" -Color White
}
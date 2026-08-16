<# 
.SYNOPSIS
    Baixa, instala Inno Setup silenciosamente e compila o instalador final
.DESCRIPTION
    Script completo: download -> install silencioso -> compila .iss -> gera .exe final
#>

param(
    [string]$Version = "1.0.0",
    [string]$InnoVersion = "6.2.2",
    [string]$InnoUrl = "https://files.jrsoftware.org/is/6/isetup-6.2.2.exe"
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$BuildDir = Join-Path $ProjectRoot "dist"
$InnoScript = Join-Path $ProjectRoot "installer.iss"
$InnoInstallerPath = "$env:TEMP\isetup-$InnoVersion.exe"
$InnoInstallDir = "${env:ProgramFiles(x86)}\Inno Setup 6"
$ISCCPath = Join-Path $InnoInstallDir "ISCC.exe"

function Write-Color($Message, $Color = "White") {
    Write-Host $Message -ForegroundColor $Color
}

function Test-IsAdmin {
    $principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Verifica se já tem iscc
if (Test-Path $ISCCPath) {
    Write-Color "[OK] Inno Setup já instalado: $ISCCPath" -Color Green
} else {
    Write-Color "[INFO] Inno Setup não encontrado. Baixando..." -Color Blue
    
    # Baixa instalador
    try {
        $wc = New-Object System.Net.WebClient
        $wc.DownloadFile($InnoUrl, $InnoInstallerPath)
        Write-Color "[OK] Download concluído" -Color Green
    } catch {
        Write-Color "[ERRO] Falha no download: $($_.Exception.Message)" -Color Red
        Write-Color "Baixe manualmente: $InnoUrl" -Color Yellow
        exit 1
    }
    
    # Verifica admin
    if (-not (Test-IsAdmin)) {
        Write-Color "[AVISO] Precisa de Admin para instalar Inno Setup." -Color Yellow
        Write-Color "Reexecute o PowerShell como Administrador e rode novamente." -Color Yellow
        exit 1
    }
    
    # Instala silenciosamente
    Write-Color "[INFO] Instalando Inno Setup silenciosamente..." -Color Blue
    $installArgs = @(
        "/VERYSILENT"
        "/SUPPRESSMSGBOXES"
        "/NORESTART"
        "/SP-"
        "/DIR=$InnoInstallDir"
    )
    
    $proc = Start-Process -FilePath $InnoInstallerPath -ArgumentList $installArgs -Wait -PassThru
    
    if ($proc.ExitCode -ne 0) {
        Write-Color "[ERRO] Falha na instalação (código: $($proc.ExitCode))" -Color Red
        exit 1
    }
    
    Write-Color "[OK] Inno Setup instalado em: $InnoInstallDir" -Color Green
    
    # Limpa instalador baixado
    Remove-Item $InnoInstallerPath -Force -ErrorAction SilentlyContinue
}

# Adiciona ao PATH da sessão atual
$env:PATH += ";$InnoInstallDir"

# Verifica iscc
if (-not (Test-Path $ISCCPath)) {
    Write-Color "[ERRO] ISCC.exe não encontrado após instalação: $ISCCPath" -Color Red
    exit 1
}

# Compila instalador
Write-Color "[INFO] Compilando instalador final com Inno Setup..." -Color Blue
Set-Location $ProjectRoot

& $ISCCPath $InnoScript

if ($LASTEXITCODE -ne 0) {
    Write-Color "[ERRO] Falha na compilação Inno Setup (código: $LASTEXITCODE)" -Color Red
    exit 1
}

Write-Color "[OK] Instalador criado com sucesso!" -Color Green

# Lista resultado
$InstallerFinal = Get-ChildItem (Join-Path $BuildDir "installer\*.exe") -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if ($InstallerFinal) {
    Write-Host ""
    Write-Color "============================================================================" -Color Cyan
    Write-Color "  INSTALADOR FINAL PRONTO" -Color Green
    Write-Color "============================================================================" -Color Cyan
    Write-Color "Arquivo: $($InstallerFinal.FullName)" -Color White
    Write-Color "Tamanho: $([math]::Round($InstallerFinal.Length/1MB, 2)) MB" -Color White
    Write-Host ""
    Write-Color "Próximos passos recomendados:" -Color Yellow
    Write-Color "1. Teste em VM Windows limpa" -Color White
    Write-Color "2. Assine digitalmente (certificado Code Signing EV)" -Color White
    Write-Color "3. Submeta ao VirusTotal: https://www.virustotal.com" -Color White
}
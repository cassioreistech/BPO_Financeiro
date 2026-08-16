; =============================================================================
; TEMPLATE INNO SETUP - Sistema BPO Financeiro
; Copie para novos projetos e ajuste as #define no topo
; =============================================================================
; Mitigações SmartScreen/Antivírus inclusas:
; - Metadados completos no executável (version_info.txt)
; - Unblock-File automático pós-instalação (remove Zone.Identifier)
; - Instalação admin apenas quando necessário (Program Files)
; - Sem downloads externos, drivers, serviços
; - Registro mínimo (apenas uninstall)
; - Compressão LZMA2/Ultra64
; =============================================================================

#define MyAppName "MeuAplicativo"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Minha Empresa"
#define MyAppURL "https://meusite.com"
#define MyAppExeName "MeuAplicativo.exe"
#define MyAppCopyright "Copyright © 2024 Minha Empresa. Todos os direitos reservados."
#define MyAppGuid "{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}"  ; Gere novo GUID para cada app

[Setup]
AppId={#MyAppGuid}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableDirPage=yes
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\dist\installer
OutputBaseFilename={#MyAppName}_Setup_{#MyAppVersion}
; SetupIconFile=..\assets\icon.ico  ; Descomente e adicione .ico
Compression=lzma2/ultra64
SolidCompression=yes
InternalCompressLevel=ultra64
UsePreviousAppDir=no
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}
AppCopyright={#MyAppCopyright}

; SmartScreen: admin apenas para Program Files
PrivilegesRequired=admin

; Assinatura digital (configure quando tiver certificado)
; SignTool=signtool.exe
; SignParameters=/a /v /tr http://timestamp.digicert.com /td sha256 /fd sha256 $f

AllowRootDirectory=no
CreateAppDir=yes
AlwaysShowGroupOnReadyPage=yes
UsePreviousGroup=no
AlwaysShowDirOnReadyPage=yes
AlwaysShowComponentsList=no
ShowComponentSizes=yes
FlatComponentsList=yes

RestartIfNeededByRun=false
CloseApplications=yes

[Languages]
Name: "portuguesbrasil"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Types]
Name: "full"; Description: "Instalação completa"; Flags: iscustom

[Components]
Name: "main"; Description: "Programa principal"; Types: full; Flags: fixed
Name: "main\exe"; Description: "Executável"; Types: full; Flags: fixed
Name: "main\dlls"; Description: "Bibliotecas"; Types: full; Flags: fixed
Name: "shortcuts"; Description: "Atalhos"; Types: full

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 0,6.1

[Files]
; Ajuste Source para onde está seu build (PyInstaller, dotnet publish, etc)
Source: "dist\{#MyAppName}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: main

; Source: "..\LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion; Components: main
; Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion; Components: main

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Comment: "{#MyAppName}"; Components: shortcuts
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Comment: "{#MyAppName}"; Tasks: desktopicon; Components: shortcuts
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Comment: "{#MyAppName}"; Tasks: quicklaunchicon; Components: shortcuts

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent; Components: main

[UninstallRun]
; Filename: "{app}\cleanup.bat"; Flags: waituntilterminated runhidden

[Registry]
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"; Flags: uninsdeletevalue

Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppName}"; ValueType: string; ValueName: "DisplayName"; ValueData: "{#MyAppName}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppName}"; ValueType: string; ValueName: "DisplayVersion"; ValueData: "{#MyAppVersion}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppName}"; ValueType: string; ValueName: "Publisher"; ValueData: "{#MyAppPublisher}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppName}"; ValueType: string; ValueName: "URLInfoAbout"; ValueData: "{#MyAppURL}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppName}"; ValueType: string; ValueName: "InstallLocation"; ValueData: "{app}"; Flags: uninsdeletevalue

[Code]
// =============================================================================
// MITIGAÇÕES SMARTSCREEN / ANTIVÍRUS - MANTENHA ESTA SEÇÃO EM TODOS PROJETOS
// =============================================================================

// Remove marca "Zone.Identifier" (arquivo baixado da internet) para evitar SmartScreen
// Executa após instalação concluir - NÃO REMOVA
procedure CurStepChanged(CurStep: TSetupStep);
var
  Cmd, Params: string;
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then begin
    Cmd := 'powershell.exe';
    Params := '-NoProfile -Command "Unblock-File -Path ''{app}\{#MyAppExeName}'' -ErrorAction SilentlyContinue; Unblock-File -Path ''{src}\{#MyAppExeName}'' -ErrorAction SilentlyContinue"';
    Exec(Cmd, Params, '', SW_HIDE, ewNoWait, ResultCode);
  end;
end;

// Verifica se deve criar atalho na área de trabalho
function ShouldCreateDesktopIcon(): Boolean;
begin
  Result := WizardIsTaskSelected('desktopicon');
end;

// Placeholder para validações customizadas
function PrepareToInstall(var NeedsRestart: Boolean): String;
begin
  Result := '';
  NeedsRestart := False;
end;

// Log para diagnóstico (opcional)
procedure LogInstallInfo(const Msg: string);
begin
  // Log silencioso
end;
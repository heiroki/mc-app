; installer/installer.iss（完全版）

#define AppName "MCApp"
#define AppVersion "1.0.0"
#define AppPublisher "Your Company"
#define AppURL "https://github.com/yourusername/mc-app"
#define AppExeName "frontend.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
OutputDir=output
OutputBaseFilename={#AppName}_Setup_v{#AppVersion}
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
WizardStyle=modern

[Languages]
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Backend
Source: "package\backend\*"; DestDir: "{app}\backend"; Flags: ignoreversion recursesubdirs createallsubdirs

; Flutter App（全ファイル）
Source: "package\flutter_app\*"; DestDir: "{app}\flutter_app"; Flags: ignoreversion recursesubdirs createallsubdirs

; Scripts
Source: "package\scripts\*.bat"; DestDir: "{app}\scripts"; Flags: ignoreversion

; VC++ Redistributable（存在する場合のみ）
Source: "VC_redist.x64.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall external skipifsourcedoesntexist

; Models（LocalAppDataにコピー）
Source: "package\models\*.gguf"; DestDir: "{localappdata}\{#AppName}\models"; Flags: ignoreversion uninsneveruninstall

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\scripts\start_app.bat"
Name: "{group}\アプリを停止"; Filename: "{app}\scripts\stop_app.bat"
Name: "{group}\ログを収集"; Filename: "{app}\scripts\collect_logs.bat"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\scripts\start_app.bat"; Tasks: desktopicon

[Run]
; VC++ Redistributableをインストール（存在する場合のみ）
Filename: "{tmp}\VC_redist.x64.exe"; Parameters: "/quiet /norestart"; StatusMsg: "Visual C++ Redistributableをインストール中..."; Flags: waituntilterminated skipifdoesntexist

; 初回起動
Filename: "{app}\scripts\start_app.bat"; Description: "{#AppName}を起動"; Flags: postinstall nowait skipifsilent

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
var
  AppDataDir: String;
begin
  if CurStep = ssPostInstall then
  begin
    AppDataDir := ExpandConstant('{localappdata}\{#AppName}');
    
    if not DirExists(AppDataDir + '\data') then
      CreateDir(AppDataDir + '\data');
    
    if not DirExists(AppDataDir + '\logs') then
      CreateDir(AppDataDir + '\logs');
    
    if not DirExists(AppDataDir + '\models') then
      CreateDir(AppDataDir + '\models');
  end;
end;
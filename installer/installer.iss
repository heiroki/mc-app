; installer/installer.iss

#define AppName "MyOllamaApp"
#define AppVersion "1.0.0"
#define AppPublisher "Your Company"
#define AppURL "https://github.com/yourusername/yourrepo"
#define AppExeName "frontend.exe"

[Setup]
; アプリケーションID（GUID生成ツールで生成推奨）
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}

; インストール先
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes

; ライセンス（オプション）
; LicenseFile=..\LICENSE

; 出力設定
OutputDir=output
OutputBaseFilename={#AppName}_Setup_v{#AppVersion}
Compression=lzma2
SolidCompression=yes

; アーキテクチャ
ArchitecturesInstallIn64BitMode=x64

; 権限（管理者権限が必要）
PrivilegesRequired=admin

; アイコン（オプション）
; SetupIconFile=icon.ico
; UninstallDisplayIcon={app}\flutter_app\{#AppExeName}

; ウィザードスタイル
WizardStyle=modern

[Languages]
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Backend
Source: "package\backend\backend_server.exe"; DestDir: "{app}\backend"; Flags: ignoreversion

; Flutter App（全ファイル）
Source: "package\flutter_app\*"; DestDir: "{app}\flutter_app"; Flags: ignoreversion recursesubdirs createallsubdirs

; Scripts
Source: "package\scripts\*.bat"; DestDir: "{app}\scripts"; Flags: ignoreversion

; VC++ Redistributable
Source: "VC_redist.x64.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall external skipifsourcedoesntexist

; Models（LocalAppDataにコピー）
Source: "package\models\*.gguf"; DestDir: "{localappdata}\{#AppName}\models"; Flags: onlyifdoesntexist uninsneveruninstall

[Icons]
; スタートメニュー
Name: "{group}\{#AppName}"; Filename: "{app}\scripts\start_app.bat"; IconFilename: "{app}\flutter_app\{#AppExeName}"
Name: "{group}\アプリを停止"; Filename: "{app}\scripts\stop_app.bat"
Name: "{group}\ログを収集"; Filename: "{app}\scripts\collect_logs.bat"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"

; デスクトップアイコン
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\scripts\start_app.bat"; IconFilename: "{app}\flutter_app\{#AppExeName}"; Tasks: desktopicon

[Run]
; VC++ Redistributableをインストール
Filename: "{tmp}\VC_redist.x64.exe"; Parameters: "/quiet /norestart"; StatusMsg: "Visual C++ Redistributableをインストール中..."; Flags: waituntilterminated skipifdoesntexist

; 初回起動（オプション）
Filename: "{app}\scripts\start_app.bat"; Description: "{#AppName}を起動"; Flags: postinstall nowait skipifsilent

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
var
  AppDataDir: String;
begin
  if CurStep = ssPostInstall then
  begin
    // アプリケーションデータディレクトリ作成
    AppDataDir := ExpandConstant('{localappdata}\{#AppName}');
    
    // 必要なディレクトリを作成
    if not DirExists(AppDataDir + '\data') then
      CreateDir(AppDataDir + '\data');
    
    if not DirExists(AppDataDir + '\logs') then
      CreateDir(AppDataDir + '\logs');
    
    if not DirExists(AppDataDir + '\models') then
      CreateDir(AppDataDir + '\models');
  end;
end;

; ============================================================
; Face Authorization System - Inno Setup Script
; ============================================================
; This script creates a Windows installer for the Face Authorization System.
;
; Requirements:
; - Inno Setup 6.x (download from https://jrsoftware.org/isdl.php)
; - Run build.py first to create the dist folder
;
; Usage:
; 1. Install Inno Setup 6
; 2. Open this file in Inno Setup Compiler
; 3. Click "Compile" or press Ctrl+F9
; ============================================================

#define MyAppName "Face Authorization System"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Your Company"
#define MyAppURL "https://github.com/your-repo"
#define MyAppExeName "FaceAuthorization.exe"

[Setup]
; Basic Info
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Installation settings
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=
OutputDir=installer
OutputBaseFilename=FaceAuthorization_Setup_{#MyAppVersion}
SetupIconFile=static\favicon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern

; Privileges (requires admin for Program Files installation)
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; Supported Windows versions
MinVersion=10.0

; Architecture
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "vietnamese"; MessagesFile: "compiler:Languages\Vietnamese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startmenuicon"; Description: "Create Start Menu shortcut"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; Main application files from PyInstaller dist folder
Source: "dist\FaceAuthorization\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Create empty data directories
Source: ""; DestDir: "{app}\data\embeddings"; Flags: skipifsourcedoesntexist
Source: ""; DestDir: "{app}\uploads"; Flags: skipifsourcedoesntexist
Source: ""; DestDir: "{app}\results"; Flags: skipifsourcedoesntexist
Source: ""; DestDir: "{app}\logs"; Flags: skipifsourcedoesntexist
Source: ""; DestDir: "{app}\index"; Flags: skipifsourcedoesntexist

[Dirs]
Name: "{app}\data"; Permissions: users-full
Name: "{app}\data\embeddings"; Permissions: users-full
Name: "{app}\uploads"; Permissions: users-full
Name: "{app}\results"; Permissions: users-full
Name: "{app}\logs"; Permissions: users-full
Name: "{app}\index"; Permissions: users-full

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Option to run after installation
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up data files on uninstall (optional - user may want to keep data)
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\uploads"
Type: filesandordirs; Name: "{app}\results"
; Don't delete data and index by default - user may want to preserve registered faces
; Type: filesandordirs; Name: "{app}\data"
; Type: filesandordirs; Name: "{app}\index"

[Code]
// Pascal Script for custom installation logic

var
  VCRedistPage: TOutputMsgMemoWizardPage;

// Check if Visual C++ Redistributable is installed
function IsVCRedistInstalled(): Boolean;
var
  Version: String;
begin
  Result := RegQueryStringValue(HKLM, 'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64', 'Version', Version);
  if not Result then
    Result := RegQueryStringValue(HKLM, 'SOFTWARE\WOW6432Node\Microsoft\VisualStudio\14.0\VC\Runtimes\x64', 'Version', Version);
end;

// Initialize wizard
procedure InitializeWizard;
begin
  // Add information page about requirements
  VCRedistPage := CreateOutputMsgMemoPage(wpWelcome,
    'System Requirements',
    'Please review the system requirements before continuing.',
    'The following components are required:',
    'Requirements:' + #13#10 +
    '- Windows 10 or later (64-bit)' + #13#10 +
    '- 4 GB RAM minimum (8 GB recommended)' + #13#10 +
    '- 2 GB free disk space' + #13#10 +
    '- Microsoft Visual C++ Redistributable 2019 or later' + #13#10 +
    #13#10 +
    'Optional for GPU acceleration:' + #13#10 +
    '- NVIDIA GPU with CUDA 11.x support' + #13#10 +
    '- CUDA Toolkit 11.x' + #13#10 +
    '- cuDNN 8.x'
  );
end;

// Check requirements before installation
function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;

  if CurPageID = VCRedistPage.ID then
  begin
    if not IsVCRedistInstalled() then
    begin
      if MsgBox('Microsoft Visual C++ Redistributable is not installed. ' +
                'The application may not work correctly without it.' + #13#10 + #13#10 +
                'Do you want to continue anyway?',
                mbConfirmation, MB_YESNO) = IDNO then
        Result := False;
    end;
  end;
end;

// Post-installation tasks
procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    // Create empty data directories if they don't exist
    if not DirExists(ExpandConstant('{app}\data\embeddings')) then
      CreateDir(ExpandConstant('{app}\data\embeddings'));
    if not DirExists(ExpandConstant('{app}\uploads')) then
      CreateDir(ExpandConstant('{app}\uploads'));
    if not DirExists(ExpandConstant('{app}\results')) then
      CreateDir(ExpandConstant('{app}\results'));
    if not DirExists(ExpandConstant('{app}\logs')) then
      CreateDir(ExpandConstant('{app}\logs'));
    if not DirExists(ExpandConstant('{app}\index')) then
      CreateDir(ExpandConstant('{app}\index'));
  end;
end;

#define MyAppName "gmIdSizing"
#define MyAppVersion "0.2"
#define MyAppPublisher "Fengqi Zhang"
#define MyAppExeName "gmIdSizing.exe"

[Setup]
AppId={{B8D4E3F1-9A2C-4D5E-8F7A-1C2B3D4E5F6A}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=.
OutputBaseFilename=gmIdSizing_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
SetupIconFile=gmId.ico
UninstallDisplayIcon={app}\gmId.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "build\runGmIdSizing.dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "build\runGmIdSizing.dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\gmId.ico"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\gmId.ico"; Tasks: desktopicon

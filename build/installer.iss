#define MyAppName "Picture Converter"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Picture Converter"
#define MyAppExeName "PictureConverter.exe"

[Setup]
AppId={{C2F3907E-7F74-4631-90BB-A7A66F63D7AF}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Picture Converter
DefaultGroupName=Picture Converter
DisableProgramGroupPage=yes
OutputDir=release
OutputBaseFilename=PictureConverter-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "release\PictureConverter\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{autoprograms}\Picture Converter"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\Picture Converter"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,Picture Converter}"; Flags: nowait postinstall skipifsilent

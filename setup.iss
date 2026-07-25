[Setup]
AppName=FlexQuiz
AppVersion=1.0.0
DefaultDirName={autopf}\FlexQuiz
DefaultGroupName=FlexQuiz
OutputDir=.
OutputBaseFilename=FlexQuiz_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64

[Files]
Source: "dist\FlexQuiz.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\FlexQuiz"; Filename: "{app}\FlexQuiz.exe"
Name: "{commondesktop}\FlexQuiz"; Filename: "{app}\FlexQuiz.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop icon"; GroupDescription: "Additional icons:";

[Registry]
Root: HKCR; Subkey: ".arnx"; ValueType: string; ValueData: "FlexQuiz.arnx"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "FlexQuiz.arnx"; ValueType: string; ValueData: "FlexQuiz Quiz Package"; Flags: uninsdeletekey
Root: HKCR; Subkey: "FlexQuiz.arnx\DefaultIcon"; ValueType: string; ValueData: "{app}\FlexQuiz.exe,0"; Flags: uninsdeletekey
Root: HKCR; Subkey: "FlexQuiz.arnx\shell\open\command"; ValueType: string; ValueData: '"{app}\FlexQuiz.exe" "%1"'; Flags: uninsdeletekey

[Run]
Filename: "{app}\FlexQuiz.exe"; Description: "Launch FlexQuiz"; Flags: nowait postinstall skipifsilent

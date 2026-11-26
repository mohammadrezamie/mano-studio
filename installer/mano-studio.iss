#ifndef BuildVersion
  #define BuildVersion "0.3.0-dev"
#endif
[Setup]
AppId=ManoStudio.Desktop
ChangesAssociations=yes
AppName=Mano Studio
AppVersion={#BuildVersion}
AppPublisher=Mano Studio contributors
AppPublisherURL=https://github.com/mohammadrezamie/mano-studio
DefaultDirName={localappdata}\Programs\Mano Studio
DefaultGroupName=Mano Studio
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=output
OutputBaseFilename=ManoStudio-Setup-v{#BuildVersion}-x64
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
SetupIconFile=..\build\mano-studio.ico
UninstallDisplayIcon={app}\ManoStudio.exe
CloseApplications=yes
RestartApplications=no
LicenseFile=..\LICENSE
[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "associate"; Description: "Associate .mano files with Mano Studio"; Flags: unchecked
[Registry]
Root: HKCU; Subkey: "Software\Classes\.mano\OpenWithProgids"; ValueType: string; ValueName: "ManoStudio.Document"; ValueData: ""; Flags: uninsdeletevalue; Tasks: associate
Root: HKCU; Subkey: "Software\Classes\ManoStudio.Document"; ValueType: string; ValueData: "Mano Studio document"; Flags: uninsdeletekey; Tasks: associate
Root: HKCU; Subkey: "Software\Classes\ManoStudio.Document\DefaultIcon"; ValueType: string; ValueData: "{app}\ManoStudio.exe,0"; Tasks: associate
Root: HKCU; Subkey: "Software\Classes\ManoStudio.Document\shell\open\command"; ValueType: string; ValueData: """{app}\ManoStudio.exe"" ""%1"""; Tasks: associate
[Files]
Source: "..\dist\ManoStudio\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
[Icons]
Name: "{group}\Mano Studio"; Filename: "{app}\ManoStudio.exe"
Name: "{group}\Uninstall Mano Studio"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Mano Studio"; Filename: "{app}\ManoStudio.exe"; Tasks: desktopicon
[Run]
Filename: "{app}\ManoStudio.exe"; Description: "{cm:LaunchProgram,Mano Studio}"; Flags: nowait postinstall skipifsilent

#ifndef BuildVersion
  #define BuildVersion "0.3.0-dev"
#endif
[Setup]
AppId=ManoStudio.Desktop
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
UninstallDisplayIcon={app}\ManoStudio.exe
CloseApplications=yes
RestartApplications=no
LicenseFile=..\LICENSE
[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
[Files]
Source: "..\dist\ManoStudio\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
[Icons]
Name: "{group}\Mano Studio"; Filename: "{app}\ManoStudio.exe"
Name: "{group}\Uninstall Mano Studio"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Mano Studio"; Filename: "{app}\ManoStudio.exe"; Tasks: desktopicon
[Run]
Filename: "{app}\ManoStudio.exe"; Description: "{cm:LaunchProgram,Mano Studio}"; Flags: nowait postinstall skipifsilent

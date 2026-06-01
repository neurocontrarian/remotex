; Inno Setup script for Commandeck Windows installer
; Free build:  iscc /DMyAppVersion=2.0.0 installer.iss
; Pro build:   iscc /DMyAppVersion=2.0.0 /DAppNameSuffix=" Pro" /DOutputSuffix="-Pro" /DAppIdGuid=C8F3D9B1-9E60-5050-A0F0-8B9CADBEEF02 installer.iss
; Note: AppIdGuid must be passed WITHOUT braces — braces are added via {{...} ISS escape syntax
; AppNameSuffix = the installed app's display name suffix (" Pro"); OutputSuffix = the
; output FILENAME suffix ("-Pro", no space) — kept separate so the download has no space.

#ifndef MyAppVersion
  #define MyAppVersion "2.0.0"
#endif
#ifndef AppNameSuffix
  #define AppNameSuffix ""
#endif
#ifndef OutputSuffix
  #define OutputSuffix ""
#endif
#ifndef AppIdGuid
  #define AppIdGuid "B7E2C8A0-8D5F-4F4E-9E2D-7A8B9C0D1E2F"
#endif

[Setup]
AppId={{{#AppIdGuid}}
AppName=Commandeck{#AppNameSuffix}
AppVersion={#MyAppVersion}
AppPublisher=neurocontrarian
AppPublisherURL=https://github.com/neurocontrarian/commandeck
AppSupportURL=https://github.com/neurocontrarian/commandeck/issues
DefaultDirName={autopf}\Commandeck{#AppNameSuffix}
DefaultGroupName=Commandeck{#AppNameSuffix}
DisableProgramGroupPage=yes
OutputDir=..\..\dist
OutputBaseFilename=Commandeck{#OutputSuffix}-{#MyAppVersion}-Windows-x64
SetupIconFile=Commandeck.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
MinVersion=10.0.17763

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
Source: "dist\Commandeck\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Commandeck{#AppNameSuffix}"; Filename: "{app}\Commandeck.exe"
Name: "{group}\Uninstall Commandeck{#AppNameSuffix}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Commandeck{#AppNameSuffix}"; Filename: "{app}\Commandeck.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Commandeck.exe"; Description: "Launch Commandeck{#AppNameSuffix}"; Flags: nowait postinstall skipifsilent

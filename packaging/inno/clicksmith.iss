; Inno Setup script for Clicksmith.
; Produces a normal Windows installer (Start Menu shortcut, optional desktop icon, uninstaller)
; around the PyInstaller build. Requires Inno Setup 6: https://jrsoftware.org/isinfo.php
;
; Build order: PyInstaller first (packaging\pyinstaller\dist\Clicksmith\Clicksmith.exe must
; exist), then:
;     iscc packaging\inno\clicksmith.iss
; AppVersion is supplied on the command line by scripts\build_windows.ps1 and the release
; workflow (ISCC /DAppVersion=1.2.3 ...); the fallback below only matters for a manual build.
#ifndef AppVersion
  #define AppVersion "1.0.2"
#endif
#define AppName "Clicksmith"
#define AppPublisher "Clicksmith contributors"
#define AppURL "https://github.com/OWNER/clicksmith"
#define DistDir "..\pyinstaller\dist\Clicksmith"

[Setup]
AppId={{B4F1C6E1-6D2B-4C7A-9E1D-6C6E2E7B3A11}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}/issues
AppUpdatesURL={#AppURL}/releases
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
OutputDir=Output
OutputBaseFilename=Clicksmith-Setup-{#AppVersion}
SetupIconFile={#DistDir}\_internal\clicksmith\assets\icon.ico
UninstallDisplayIcon={app}\Clicksmith.exe
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64compatible
LicenseFile=..\..\LICENSE

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Files]
Source: "{#DistDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\Clicksmith.exe"
Name: "{group}\Uninstall {#AppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\Clicksmith.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Clicksmith.exe"; Description: "Launch {#AppName} now"; Flags: nowait postinstall skipifsilent unchecked

[UninstallDelete]
; Removes logs and the config file if the person installed in "portable" mode inside {app};
; per-user AppData settings/profiles are left in place so a reinstall does not lose them.
Type: filesandordirs; Name: "{app}\data"

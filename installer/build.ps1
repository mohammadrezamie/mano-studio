param([switch]$PortableOnly, [switch]$ReuseFrozen)
$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '..')
if (-not [Environment]::Is64BitProcess) { throw 'Use 64-bit Python and PowerShell.' }
$version = (python -c "from update_service import VERSION; print(VERSION)").Trim()
if ($LASTEXITCODE -ne 0 -or $version -notmatch '^\d+\.\d+\.\d+-(dev|alpha|beta|rc)(\.\d+)?) {
    throw 'Only explicitly marked development/prerelease builds are allowed.'
}
$icon = Join-Path $PWD 'build\mano-studio.ico'
if (-not $ReuseFrozen) {
python -m installer.build_icon $icon
if ($LASTEXITCODE -ne 0 -or !(Test-Path $icon)) { throw 'Brand icon generation failed.' }
if (Test-Path 'dist\ManoStudio') { Remove-Item 'dist\ManoStudio' -Recurse -Force }
python -m PyInstaller --noconfirm --clean --onedir --windowed --icon $icon --name ManoStudio --add-data 'rtl_translator.py;.' --add-data 'LICENSE;.' --add-data 'examples;examples' --add-data 'docs;docs' main.py
if ($LASTEXITCODE -ne 0) { throw 'PyInstaller failed.' }
$dist = Join-Path $PWD 'dist\ManoStudio'
$notices = Join-Path $dist 'third-party-notices'
New-Item -ItemType Directory -Force $notices | Out-Null
# Preserve notices shipped in the installed distributions; legal review is still required before public release.
python installer/collect_notices.py $notices
if ($LASTEXITCODE -ne 0) { throw 'Notice collection failed.' }
}
if (-not (Test-Path 'dist\ManoStudio\ManoStudio.exe')) { throw 'Frozen app missing.' }
if ($PortableOnly) { exit 0 }
if (!(Test-Path $icon)) { throw 'Candidate brand icon missing; build portable first.' }
$compiler = Join-Path ${env:ProgramFiles(x86)} 'Inno Setup 6\ISCC.exe'
if (-not (Test-Path $compiler)) {
    $cmd = Get-Command ISCC.exe -ErrorAction SilentlyContinue
    if (-not $cmd) { throw 'Install Inno Setup 6 before building.' }
    $compiler = $cmd.Source
}
if (Test-Path 'installer\output') {
    Get-ChildItem 'installer\output' -Filter 'ManoStudio-Setup-*-x64.exe*' | Remove-Item -Force
}
& $compiler "/DBuildVersion=$version" 'installer\mano-studio.iss'
if ($LASTEXITCODE -ne 0) { throw 'Inno Setup failed.' }
) {
    throw 'Only explicitly marked 0.x development/prerelease builds are allowed.'
}
$icon = Join-Path $PWD 'build\mano-studio.ico'
if (-not $ReuseFrozen) {
python -m installer.build_icon $icon
if ($LASTEXITCODE -ne 0 -or !(Test-Path $icon)) { throw 'Brand icon generation failed.' }
if (Test-Path 'dist\ManoStudio') { Remove-Item 'dist\ManoStudio' -Recurse -Force }
python -m PyInstaller --noconfirm --clean --onedir --windowed --icon $icon --name ManoStudio --add-data 'rtl_translator.py;.' --add-data 'LICENSE;.' --add-data 'examples;examples' --add-data 'docs;docs' main.py
if ($LASTEXITCODE -ne 0) { throw 'PyInstaller failed.' }
$dist = Join-Path $PWD 'dist\ManoStudio'
$notices = Join-Path $dist 'third-party-notices'
New-Item -ItemType Directory -Force $notices | Out-Null
# Preserve notices shipped in the installed distributions; legal review is still required before public release.
python installer/collect_notices.py $notices
if ($LASTEXITCODE -ne 0) { throw 'Notice collection failed.' }
}
if (-not (Test-Path 'dist\ManoStudio\ManoStudio.exe')) { throw 'Frozen app missing.' }
if ($PortableOnly) { exit 0 }
if (!(Test-Path $icon)) { throw 'Candidate brand icon missing; build portable first.' }
$compiler = Join-Path ${env:ProgramFiles(x86)} 'Inno Setup 6\ISCC.exe'
if (-not (Test-Path $compiler)) {
    $cmd = Get-Command ISCC.exe -ErrorAction SilentlyContinue
    if (-not $cmd) { throw 'Install Inno Setup 6 before building.' }
    $compiler = $cmd.Source
}
if (Test-Path 'installer\output') {
    Get-ChildItem 'installer\output' -Filter 'ManoStudio-Setup-*-x64.exe*' | Remove-Item -Force
}
& $compiler "/DBuildVersion=$version" 'installer\mano-studio.iss'
if ($LASTEXITCODE -ne 0) { throw 'Inno Setup failed.' }

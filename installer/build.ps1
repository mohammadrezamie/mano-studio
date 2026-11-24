$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '..')
if (-not [Environment]::Is64BitProcess) { throw 'Use 64-bit Python and PowerShell.' }
$version = (python -c "from update_service import VERSION; print(VERSION)").Trim()
if ($LASTEXITCODE -ne 0 -or $version -notmatch '^0\.\d+\.\d+-(dev|alpha|beta|rc)(\.\d+)?$') {
    throw 'Only explicitly marked 0.x development/prerelease builds are allowed.'
}
python -m PyInstaller --noconfirm --clean --onedir --windowed --name ManoStudio --add-data 'rtl_translator.py:.' --add-data 'LICENSE:.' --add-data 'examples:examples' --add-data 'docs:docs' main.py
if ($LASTEXITCODE -ne 0) { throw 'PyInstaller failed.' }
$dist = Join-Path $PWD 'dist\ManoStudio'
$notices = Join-Path $dist 'third-party-notices'
New-Item -ItemType Directory -Force $notices | Out-Null
# Preserve notices shipped in the installed distributions; legal review is still required before public release.
python installer/collect_notices.py $notices
if ($LASTEXITCODE -ne 0) { throw 'Notice collection failed.' }
$compiler = Join-Path ${env:ProgramFiles(x86)} 'Inno Setup 6\ISCC.exe'
if (-not (Test-Path $compiler)) {
    $cmd = Get-Command ISCC.exe -ErrorAction SilentlyContinue
    if (-not $cmd) { throw 'Install Inno Setup 6 before building.' }
    $compiler = $cmd.Source
}
& $compiler "/DBuildVersion=$version" 'installer\mano-studio.iss'
if ($LASTEXITCODE -ne 0) { throw 'Inno Setup failed.' }

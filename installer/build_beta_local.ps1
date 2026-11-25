# Run only on a disposable, clean Windows x64 VM with Git, Python 3.12 x64,
# PowerShell 7 and Inno Setup 6 installed. Never publishes or signs anything.
param([Parameter(Mandatory=$true)][string]$ExpectedSha,
      [Parameter(Mandatory=$true)][switch]$DisposableVm)
$ErrorActionPreference = 'Stop'
if (-not $DisposableVm) { throw 'Use a disposable VM; smoke.ps1 installs and uninstalls the app.' }
if ($ExpectedSha -notmatch '^[a-f0-9]{40}$') { throw 'Supply the full expected source SHA.' }
if (-not $IsWindows -or -not [Environment]::Is64BitProcess) { throw 'Use Windows x64 PowerShell 7.' }
Set-Location (Join-Path $PSScriptRoot '..')
function Checked([string]$Program, [string[]]$Arguments) {
    & $Program @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Failed: $Program (exit $LASTEXITCODE)" }
}
$sha = (git rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $sha -cne $ExpectedSha) { throw 'Source revision mismatch.' }
if (git status --porcelain) { throw 'Start from a clean checkout.' }
if ($LASTEXITCODE -ne 0) { throw 'Cannot verify clean checkout.' }
$env:RUNNER_TEMP = Join-Path ([IO.Path]::GetTempPath()) ('mano-beta-' + [Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $env:RUNNER_TEMP | Out-Null
$env:QT_QPA_PLATFORM = 'offscreen'
$env:QT_QPA_FONTDIR = Join-Path $env:WINDIR 'Fonts'
$env:MANO_SOURCE_SHA = $sha
if (Test-Path '.venv-beta') { throw 'Use a new checkout without a previous build environment.' }
Checked 'py' @('-3.12','-m','venv','.venv-beta')
$env:PATH = (Join-Path $PWD '.venv-beta\Scripts') + ';' + $env:PATH
Checked 'python' @('-c','import sys,struct; assert sys.version_info[:2]==(3,12) and struct.calcsize("P")==8')
Checked 'python' @('-m','pip','install','-r','requirements.txt','-r','requirements-dev.txt','-r','requirements-build.txt')
$version = (python -c 'from update_service import VERSION; print(VERSION)').Trim()
if ($LASTEXITCODE -ne 0 -or $version -cne '0.3.0-beta.1') { throw 'Unexpected beta version.' }
Checked 'python' @('render_preflight.py')
Checked 'python' @('-m','pytest','-q','--durations=25')
Checked 'python' @('capture_workspace.py')
Checked 'pwsh' @('-NoProfile','-File','installer/build.ps1','-PortableOnly')
$report = Join-Path $env:RUNNER_TEMP 'mano-portable-smoke.txt'
$app = Join-Path $PWD 'dist\ManoStudio\ManoStudio.exe'
$p = Start-Process -FilePath $app -ArgumentList "--smoke-test `"$report`"" -PassThru
if (-not $p.WaitForExit(120000)) { $p.Kill(); throw 'Portable smoke timed out.' }
if ($p.ExitCode -ne 0 -or !(Test-Path $report) -or (Get-Content $report -Raw).Trim() -ne 'PASS') { throw 'Portable smoke failed.' }
New-Item -ItemType Directory -Force portable-output | Out-Null
$zip = "portable-output/ManoStudio-v$version-Windows-x64.zip"
Checked 'python' @('-c',"import shutil,sys; shutil.make_archive(sys.argv[1],'zip',root_dir='dist',base_dir='ManoStudio')",($zip -replace '\.zip$',''))
(Get-FileHash $zip -Algorithm SHA256).Hash.ToLower() | Set-Content -Encoding ascii "$zip.sha256"
Checked 'pwsh' @('-NoProfile','-File','installer/build.ps1','-ReuseFrozen')
Checked 'pwsh' @('-NoProfile','-File','installer/smoke.ps1')
$dependencies = @(python -m pip freeze)
if ($LASTEXITCODE -ne 0 -or $dependencies.Count -eq 0) { throw 'Dependency manifest failed.' }
foreach ($folder in @('portable-output','installer/output')) {
    $dependencies | Set-Content -Encoding utf8 (Join-Path $folder 'build-dependencies.txt')
    "SHA=$sha" | Set-Content -Encoding ascii (Join-Path $folder 'commit.txt')
    Copy-Item $report (Join-Path $folder 'portable-smoke.txt')
}
Copy-Item (Join-Path $env:RUNNER_TEMP 'mano-smoke.txt') installer/output/installed-smoke.txt
$setups = @(Get-ChildItem installer/output/ManoStudio-Setup-*-x64.exe)
if ($setups.Count -ne 1) { throw 'Expected exactly one setup.' }
foreach ($setup in $setups) {
    $hash = (Get-FileHash $setup.FullName -Algorithm SHA256).Hash.ToLower()
    "$hash  $($setup.Name)" | Set-Content -Encoding ascii "$($setup.FullName).sha256"
}
Checked 'python' @('installer/candidate_manifest.py','--root','.','--sha',$sha)
Write-Host 'Candidate evidence written to portable-output, installer/output and screenshots.'
Write-Host 'Not published. Native UX, Linux regression, redistribution and release acceptance still required.'

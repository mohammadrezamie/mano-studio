$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '..')
$setups = @(Get-ChildItem 'installer\output\ManoStudio-Setup-*-x64.exe')
if ($setups.Count -ne 1) { throw 'Expected exactly one fresh installer.' }
$setup = $setups[0]
$target = Join-Path $env:RUNNER_TEMP ('Mano Studio Smoke ' + [Guid]::NewGuid().ToString('N'))
$report = Join-Path $env:RUNNER_TEMP 'mano-smoke.txt'
$env:QT_QPA_PLATFORM = 'offscreen'
if (Test-Path $report) { Remove-Item $report -Force }
if (Test-Path $target) { throw 'Smoke installation must start in a new directory.' }
function Run-Checked($file, $arguments) {
    $p = Start-Process -FilePath $file -ArgumentList $arguments -PassThru
    if (-not $p.WaitForExit(120000)) { $p.Kill(); throw "Process timed out: $file" }
    if ($p.ExitCode -ne 0) { throw "Exit $($p.ExitCode): $file" }
}
Run-Checked $setup.FullName "/VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP- /DIR=`"$target`""
try {
    Run-Checked (Join-Path $target 'ManoStudio.exe') "--smoke-test `"$report`""
    if (!(Test-Path $report) -or (Get-Content $report -Raw).Trim() -ne 'PASS') { throw 'Frozen app smoke test failed.' }
} finally {
    Run-Checked (Join-Path $target 'unins000.exe') '/VERYSILENT /SUPPRESSMSGBOXES /NORESTART'
}
if (Test-Path (Join-Path $target 'ManoStudio.exe')) { throw 'Uninstall left executable.' }
Write-Host 'Install, frozen application smoke test, and uninstall passed.'

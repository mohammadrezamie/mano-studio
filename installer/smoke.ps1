$ErrorActionPreference = 'Stop'
if ($env:GITHUB_ACTIONS -ne 'true' -or !$env:RUNNER_TEMP) { throw 'Run this installer smoke only on a disposable GitHub Actions Windows runner.' }
Set-Location (Join-Path $PSScriptRoot '..')
$setups = @(Get-ChildItem 'installer\output\ManoStudio-Setup-*-x64.exe')
if ($setups.Count -ne 1) { throw 'Expected exactly one fresh installer.' }
$setup = $setups[0]
$target = Join-Path $env:RUNNER_TEMP ('Mano Studio Smoke ' + [Guid]::NewGuid().ToString('N'))
$report = Join-Path $env:RUNNER_TEMP 'mano-smoke.txt'
$payloadReport = Join-Path $env:RUNNER_TEMP 'mano-installed-payload.json'
if (Test-Path $payloadReport) { Remove-Item $payloadReport -Force }
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
    python -m installer.verify_installed --frozen (Join-Path $PWD 'dist\ManoStudio') --installed $target --report $payloadReport
    if ($LASTEXITCODE -ne 0 -or !(Test-Path $payloadReport)) { throw 'Installed payload verification failed.' }
    $source = @(Get-ChildItem -LiteralPath $target -Recurse -File -Filter 'rtl_translator.py')
    if ($source.Count -ne 1) { throw 'Expected exactly one installed academic source.' }
    $expected = (Get-FileHash -LiteralPath (Join-Path $PWD 'rtl_translator.py') -Algorithm SHA256).Hash
    if ((Get-FileHash -LiteralPath $source[0].FullName -Algorithm SHA256).Hash -ne $expected) { throw 'Installed academic source does not match checkout.' }
    # Remove developer tool paths for the installed application launch only.
    $savedEnvironment = @{}
    $names = @('PATH','PYTHONHOME','PYTHONPATH','QT_PLUGIN_PATH','QT_QPA_PLATFORM_PLUGIN_PATH','QT_QPA_FONTDIR','QML_IMPORT_PATH','QML2_IMPORT_PATH','VIRTUAL_ENV','CONDA_PREFIX')
    foreach ($name in $names) {
        $savedEnvironment[$name] = [Environment]::GetEnvironmentVariable($name, 'Process')
    }
    try {
        $env:PATH = "$env:SystemRoot\System32;$env:SystemRoot"
        foreach ($name in $names) {
            if ($name -ne 'PATH') { [Environment]::SetEnvironmentVariable($name, $null, 'Process') }
        }
        Push-Location $target
        try {
            Run-Checked (Join-Path $target 'ManoStudio.exe') "--smoke-test `"$report`""
            $probe = Join-Path $env:RUNNER_TEMP 'mano-standalone-runtime.json'
            if (Test-Path $probe) { Remove-Item $probe -Force }
            Run-Checked (Join-Path $target 'ManoStudio.exe') "--runtime-probe `"$probe`""
            if (!(Test-Path $probe)) { throw 'Missing standalone runtime report.' }
        } finally { Pop-Location }
    } finally {
        foreach ($name in $names) {
            [Environment]::SetEnvironmentVariable($name, $savedEnvironment[$name], 'Process')
        }
    }
    if (!(Test-Path $report) -or (Get-Content $report -Raw).Trim() -ne 'PASS') { throw 'Frozen app smoke test failed.' }
} finally {
    Run-Checked (Join-Path $target 'unins000.exe') '/VERYSILENT /SUPPRESSMSGBOXES /NORESTART'
}
if (Test-Path (Join-Path $target 'ManoStudio.exe')) { throw 'Uninstall left executable.' }
Write-Host 'Install, frozen application smoke test, and uninstall passed.'

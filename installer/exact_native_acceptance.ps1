param([Parameter(Mandatory=$true)][string]$Setup,[Parameter(Mandatory=$true)][string]$ExpectedHash,[Parameter(Mandatory=$true)][string]$Profile)
$ErrorActionPreference='Stop'
if ($env:GITHUB_ACTIONS -ne 'true' -or $env:RUNNER_OS -ne 'Windows' -or !$env:RUNNER_TEMP) {throw 'Disposable Windows Actions runner required'}
if ($Profile -notin @('isolated-path','pre-equipped')) {throw 'Unknown profile'}
$setupPath=(Resolve-Path -LiteralPath $Setup).Path
if ((Get-FileHash -LiteralPath $setupPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $ExpectedHash) {throw 'Wrong exact installer'}
$target=Join-Path $env:RUNNER_TEMP ('Mano Acceptance '+[Guid]::NewGuid().ToString('N'))
$userFile=Join-Path $env:RUNNER_TEMP ('mano-user-'+[Guid]::NewGuid().ToString('N')+'.rtl')
$reportDir=Join-Path $PWD 'native-evidence'
New-Item -ItemType Directory -Force $reportDir | Out-Null
$reg='HKCU:\Software\ManoStudio\ManoStudio'
$uninstallAttempted=$false
if (Test-Path $reg) {throw 'Expected a fresh application settings profile'}
if (Test-Path $target) {throw 'Unexpected installation target'}
$names=@('PATH','PYTHONHOME','PYTHONPATH','QT_PLUGIN_PATH','QT_QPA_PLATFORM_PLUGIN_PATH','QT_QPA_FONTDIR','QML_IMPORT_PATH','QML2_IMPORT_PATH','VIRTUAL_ENV','CONDA_PREFIX','QT_QPA_PLATFORM')
$saved=@{}
foreach($name in $names){$saved[$name]=[Environment]::GetEnvironmentVariable($name,'Process')}
function Run-Checked($file,$argsText) {
  $p=Start-Process -FilePath $file -ArgumentList $argsText -PassThru
  if(!$p.WaitForExit(120000)){$p.Kill();throw "Process timed out: $file"}
  if($p.ExitCode -ne 0){throw "Process failed ($($p.ExitCode)): $file"}
}
function Install-Exact {
  $argsText='/VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP- /DIR="'+$target+'" /TASKS=""'
  Run-Checked $setupPath $argsText
}
function Smoke($phase) {
  $report=Join-Path $reportDir ($phase+'.txt')
  Run-Checked (Join-Path $target 'ManoStudio.exe') ('--smoke-test "'+$report+'"')
  if(!(Test-Path $report) -or (Get-Content -LiteralPath $report -Raw).Trim() -ne 'PASS'){throw "Smoke failed: $phase"}
}
try {
  if($Profile -eq 'isolated-path'){
    $env:PATH="$env:SystemRoot\System32;$env:SystemRoot"
    foreach($name in $names){if($name -ne 'PATH'){[Environment]::SetEnvironmentVariable($name,$null,'Process')}}
  }
  $env:QT_QPA_PLATFORM='offscreen'
  Install-Exact
  Smoke 'first-install'
  New-Item -Path $reg -Force | Out-Null
  New-ItemProperty -Path $reg -Name 'language' -Value 'fa' -PropertyType String -Force | Out-Null
  Set-Content -LiteralPath $userFile -Value 'AC <- M[100]' -Encoding ascii
  $userHash=(Get-FileHash -LiteralPath $userFile -Algorithm SHA256).Hash
  Install-Exact
  Smoke 'same-version-reinstall'
  if((Get-ItemProperty -Path $reg -Name language).language -ne 'fa'){throw 'Settings not preserved'}
  if((Get-FileHash -LiteralPath $userFile -Algorithm SHA256).Hash -ne $userHash){throw 'Document changed'}
  $uninstallAttempted=$true
  Run-Checked (Join-Path $target 'unins000.exe') '/VERYSILENT /SUPPRESSMSGBOXES /NORESTART'
  if(Test-Path (Join-Path $target 'ManoStudio.exe')){throw 'Uninstall left executable'}
  if((Get-FileHash -LiteralPath $userFile -Algorithm SHA256).Hash -ne $userHash){throw 'Uninstall changed document'}
  @{installer_sha256=$ExpectedHash; profile=$Profile; fresh_target=$true; fresh_settings=$true; first_install='pass'; same_version_reinstall='pass'; settings_preserved=$true; document_preserved=$true; uninstall='pass'; bare_os_verified=$false; cross_version_upgrade_verified=$false; interactive_visual_verified=$false} | ConvertTo-Json | Set-Content -Encoding utf8 (Join-Path $reportDir 'summary.json')
} finally {
  foreach($name in $names){[Environment]::SetEnvironmentVariable($name,$saved[$name],'Process')}
  if(!$uninstallAttempted -and (Test-Path (Join-Path $target 'unins000.exe'))){
    try { Run-Checked (Join-Path $target 'unins000.exe') '/VERYSILENT /SUPPRESSMSGBOXES /NORESTART' }
    catch { Write-Warning "Best-effort cleanup failed: $_" }
  }
}

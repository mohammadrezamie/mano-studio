param([string]$Archive,[string]$ExpectedHash)
$ErrorActionPreference='Stop'
if ($env:GITHUB_ACTIONS -ne 'true' -or $env:RUNNER_OS -ne 'Windows' -or !$env:RUNNER_TEMP) {throw 'Disposable Windows runner required'}
$archive=(Resolve-Path -LiteralPath $Archive).Path
if ((Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant() -ne $ExpectedHash){throw 'Archive identity mismatch'}
$root=Join-Path $env:RUNNER_TEMP ('mano-lean-'+[Guid]::NewGuid().ToString('N'))
$out=Join-Path $PWD 'lean-evidence'
New-Item -ItemType Directory -Force $out | Out-Null
$names=@('Qt6Qml.dll','Qt6QmlMeta.dll','Qt6QmlModels.dll','Qt6QmlWorkerScript.dll','Qt6Quick.dll')
$removed=@()
$env:QT_QPA_PLATFORM='offscreen'
$env:QT_QPA_FONTDIR=Join-Path $env:WINDIR 'Fonts'
function Smoke($label) {
  $report=Join-Path $out ($label+'.txt')
  $p=Start-Process -FilePath (Join-Path $root 'ManoStudio\ManoStudio.exe') -ArgumentList ('--smoke-test "'+$report+'"') -PassThru
  if(!$p.WaitForExit(120000)){$p.Kill();throw "Timeout: $label"}
  if($p.ExitCode -ne 0 -or !(Test-Path $report) -or (Get-Content -LiteralPath $report -Raw).Trim() -ne 'PASS'){throw "Smoke failed: $label"}
}
try {
  Expand-Archive -LiteralPath $archive -DestinationPath $root
  Smoke 'original'
  foreach($name in $names){
    $file=Join-Path $root ('ManoStudio\_internal\PySide6\'+$name)
    if(!(Test-Path -LiteralPath $file -PathType Leaf)){throw "Expected dependency not found: $name"}
    $removed+=@{name=$name; bytes=(Get-Item -LiteralPath $file).Length; sha256=(Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLowerInvariant()}
    Remove-Item -LiteralPath $file -Force
  }
  Smoke 'without-qml'
  @{archive_sha256=$ExpectedHash; original_smoke='pass'; pruned_smoke='pass'; removed=$removed; publication_approved=$false; full_feature_regression=$false; dynamic_load_proof=$false} | ConvertTo-Json -Depth 5 | Set-Content -Encoding utf8 (Join-Path $out 'report.json')
} finally {
  if(Test-Path $root){Remove-Item -LiteralPath $root -Recurse -Force}
}

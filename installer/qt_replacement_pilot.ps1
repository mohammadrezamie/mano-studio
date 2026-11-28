param([Parameter(Mandatory)][string]$Archive,[Parameter(Mandatory)][string]$ExpectedHash)
$ErrorActionPreference='Stop'
if ($env:GITHUB_ACTIONS -ne 'true' -or $env:RUNNER_OS -ne 'Windows' -or !$env:RUNNER_TEMP) {throw 'Disposable Windows CI only'}
$archive=(Resolve-Path -LiteralPath $Archive).Path
if((Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant() -ne $ExpectedHash){throw 'Candidate archive changed'}
$root=Join-Path $env:RUNNER_TEMP ('mano-qt-replacement-'+[Guid]::NewGuid().ToString('N'))
$out=Join-Path $PWD 'replacement-evidence'
New-Item -ItemType Directory -Force $out | Out-Null
$env:QT_QPA_PLATFORM='offscreen'
$env:QT_QPA_FONTDIR=Join-Path $env:WINDIR 'Fonts'
function Smoke([string]$label){
    $report=Join-Path $out ($label+'.txt')
    $p=Start-Process -FilePath (Join-Path $root 'ManoStudio\ManoStudio.exe') -ArgumentList ('--smoke-test "'+$report+'"') -PassThru
    if(!$p.WaitForExit(120000)){$p.Kill();throw "Smoke timeout: $label"}
    if($p.ExitCode -ne 0 -or !(Test-Path $report) -or (Get-Content -LiteralPath $report -Raw).Trim() -ne 'PASS'){throw "Smoke failed: $label"}
}
try {
    Expand-Archive -LiteralPath $archive -DestinationPath $root
    $dll=Join-Path $root 'ManoStudio\_internal\PySide6\Qt6Core.dll'
    $before=(Get-FileHash -LiteralPath $dll -Algorithm SHA256).Hash.ToLowerInvariant()
    if($before -ne 'f57ed38afd95d0306cca9d88d997f639f70c7628a4f1f064eae291d579487121'){throw 'Unexpected QtCore bytes'}
    Smoke 'original'
    # Only a disposable test copy is changed. No code sections are modified.
    $backup=Join-Path $root 'qtcore-original.bin'
    $replacement=Join-Path $root 'qtcore-pilot.bin'
    Copy-Item -LiteralPath $dll -Destination $backup
    Copy-Item -LiteralPath $dll -Destination $replacement
    $stream=[System.IO.File]::Open($replacement,[System.IO.FileMode]::Append,[System.IO.FileAccess]::Write)
    try {
        $marker=[System.Text.Encoding]::ASCII.GetBytes('ManoStudio-CI-replacement-pilot-v1')
        $stream.Write($marker,0,$marker.Length)
    } finally {$stream.Dispose()}
    $after=(Get-FileHash -LiteralPath $replacement -Algorithm SHA256).Hash.ToLowerInvariant()
    if($before -eq $after){throw 'Replacement did not change bytes'}
    Move-Item -LiteralPath $replacement -Destination $dll -Force
    if((Get-FileHash -LiteralPath $dll -Algorithm SHA256).Hash.ToLowerInvariant() -ne $after){throw 'Replacement mismatch'}
    Smoke 'replacement'
    Copy-Item -LiteralPath $backup -Destination $dll -Force
    if((Get-FileHash -LiteralPath $dll -Algorithm SHA256).Hash.ToLowerInvariant() -ne $before){throw 'Restoration failed'}
    Smoke 'restored'
    @{candidate_sha256=$ExpectedHash; original_qtcore_sha256=$before; replacement_qtcore_sha256=$after; original_smoke='pass'; replacement_smoke='pass'; restored_smoke='pass'; method='non-code overlay in disposable CI copy'; source_rebuilt_library_test=$false; source_correspondence_verified=$false; redistribution_approved=$false} | ConvertTo-Json | Set-Content -Encoding utf8 (Join-Path $out 'report.json')
} finally {
    if(Test-Path $root){Remove-Item -LiteralPath $root -Recurse -Force}
}

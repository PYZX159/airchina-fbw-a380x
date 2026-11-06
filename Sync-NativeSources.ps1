$ErrorActionPreference = 'Stop'
$sourceRoot = Join-Path $PSScriptRoot 'artwork\final'
$textureRoot = Join-Path $PSScriptRoot 'project\PackageSources\SimObjects\airplanes\FlyByWire_A380X\liveries\eason\AirChina_Fictional_B38AC\texture'
$nameMap = Import-Csv -LiteralPath (Join-Path $PSScriptRoot 'resources\official-scripts\rename_list.csv')
$copiedNames = @()
foreach ($taskPng in Get-ChildItem -LiteralPath $sourceRoot -File -Filter '*.PNG') {
    $taskMapping = @($nameMap | Where-Object current_name -IEQ $taskPng.Name)
    if ($taskMapping.Count -ne 1) { throw "Missing or ambiguous official name mapping for $($taskPng.Name)" }
    $taskDestination = Join-Path $textureRoot $taskMapping[0].new_name
    Copy-Item -LiteralPath $taskPng.FullName -Destination $taskDestination -Force
    $copiedNames += $taskMapping[0].new_name
}
if ($copiedNames.Count -ne 9) { throw "Expected 9 custom texture sheets; copied $($copiedNames.Count)." }
Write-Output ('Updated Native SDK source PNGs: ' + ($copiedNames -join ', '))

param(
    [string]$PackagePath = (Join-Path $PSScriptRoot 'package\airchina-fbw-a380x-stable')
)

# MSFS legacy textures require a compiled bitmap descriptor beside each DDS.
# GIMP exports the DDS image, but does not generate the MSFS-specific JSON.
$ErrorActionPreference = 'Stop'
$textureRoot = Join-Path $PackagePath 'SimObjects\AirPlanes\FlyByWire_A380_842_AirChina_Fictional\texture.AIRCHINA'
$sourceRoot = Join-Path $PSScriptRoot 'artwork\final'
$writtenDescriptors = 0
foreach ($taskDds in Get-ChildItem -LiteralPath $textureRoot -File -Filter '*.DDS') {
    $taskSourceName = [System.IO.Path]::GetFileNameWithoutExtension($taskDds.Name)
    $taskSourcePath = Join-Path $sourceRoot $taskSourceName
    $taskSourceDate = if (Test-Path -LiteralPath $taskSourcePath -PathType Leaf) {
        (Get-Item -LiteralPath $taskSourcePath).LastWriteTimeUtc.ToFileTimeUtc()
    } else {
        $taskDds.LastWriteTimeUtc.ToFileTimeUtc()
    }
    $taskDescriptor = [ordered]@{
        Version = 2
        SourceFileDate = [int64]$taskSourceDate
        Flags = @('FL_BITMAP_COMPRESSION', 'FL_BITMAP_MIPMAP')
    }
    if ($taskDds.Name -ieq 'A380X_REGISTRATION_ALBEDO.PNG.DDS') {
        $taskDescriptor.HasTransp = $true
    }
    $taskJson = $taskDescriptor | ConvertTo-Json -Compress -Depth 4
    [System.IO.File]::WriteAllText($taskDds.FullName + '.json', $taskJson, [System.Text.UTF8Encoding]::new($false))
    $writtenDescriptors++
}
if ($writtenDescriptors -ne 9) { throw "Expected nine DDS descriptors; wrote $writtenDescriptors." }
Write-Output "Wrote $writtenDescriptors MSFS DDS texture descriptors."

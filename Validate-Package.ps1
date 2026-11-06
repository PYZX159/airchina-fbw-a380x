param(
    [string]$PackagePath = (Join-Path $PSScriptRoot 'package\airchina-fbw-a380x-stable'),
    [string]$BasePackagePath = $env:FBW_A380X_BASE_PATH
)

# Read-only structural validation. This script never creates, updates or installs files.
$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($BasePackagePath)) {
    throw 'Supply -BasePackagePath pointing to flybywire-aircraft-a380-842, or set FBW_A380X_BASE_PATH.'
}
$validationErrors = [System.Collections.Generic.List[string]]::new()
$validationWarnings = [System.Collections.Generic.List[string]]::new()
$packageRoot = [System.IO.Path]::GetFullPath($PackagePath)
$baseRoot = [System.IO.Path]::GetFullPath($BasePackagePath)
$aircraftName = 'FlyByWire_A380_842_AirChina_Fictional'
$aircraftRelative = "SimObjects\AirPlanes\$aircraftName"
$aircraftRoot = Join-Path $packageRoot $aircraftRelative
$textureRoot = Join-Path $aircraftRoot 'texture.AIRCHINA'

function Assert-Valid([bool]$Condition, [string]$Message) {
    if (-not $Condition) { $validationErrors.Add($Message) }
}

function Read-Cfg([string]$CfgPath) {
    $sections = @{}
    $section = ''
    foreach ($line in [System.IO.File]::ReadAllLines($CfgPath)) {
        $text = ($line -split ';',2)[0].Trim()
        if (-not $text) { continue }
        if ($text -match '^\[([^\]]+)\]$') {
            $section = $Matches[1]
            if (-not $sections.ContainsKey($section)) { $sections[$section] = @{} }
        } elseif ($text -match '^([^=]+)=(.*)$') {
            if (-not $sections.ContainsKey($section)) { $sections[$section] = @{} }
            $sections[$section][$Matches[1].Trim()] = $Matches[2].Trim().Trim('"')
        }
    }
    return $sections
}

function Resolve-VfsReference([string]$RelativeDirectory, [string]$Reference) {
    $virtualDirectory = Join-Path (Join-Path $baseRoot 'SimObjects\AirPlanes') $RelativeDirectory
    return [System.IO.Path]::GetFullPath((Join-Path $virtualDirectory $Reference))
}

try {
    $manifestPath = Join-Path $packageRoot 'manifest.json'
    $layoutPath = Join-Path $packageRoot 'layout.json'
    $manifest = [System.IO.File]::ReadAllText($manifestPath) | ConvertFrom-Json
    $layout = [System.IO.File]::ReadAllText($layoutPath) | ConvertFrom-Json
    Assert-Valid ($manifest.content_type -eq 'LIVERY') 'manifest content_type must be LIVERY.'
    $dependency = @($manifest.dependencies | Where-Object name -eq 'flybywire-aircraft-a380-842')
    Assert-Valid ($dependency.Count -eq 1) 'The manifest must depend on flybywire-aircraft-a380-842 once.'
    if ($dependency.Count -eq 1) {
        Assert-Valid ($dependency[0].package_version -eq '2024.1.0') 'Expected Stable base dependency version 2024.1.0.'
    }

    $indexedPaths = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
    [int64]$indexedBytes = 0
    foreach ($entry in @($layout.content)) {
        $relativePath = [string]$entry.path
        Assert-Valid (-not [string]::IsNullOrWhiteSpace($relativePath)) 'layout contains an empty path.'
        if ([string]::IsNullOrWhiteSpace($relativePath)) { continue }
        Assert-Valid (-not [System.IO.Path]::IsPathRooted($relativePath)) "Absolute path in layout: $relativePath"
        $resolvedPath = [System.IO.Path]::GetFullPath((Join-Path $packageRoot $relativePath))
        $insidePackage = $resolvedPath.StartsWith($packageRoot + '\',[System.StringComparison]::OrdinalIgnoreCase)
        Assert-Valid $insidePackage "Path escapes package: $relativePath"
        if (-not $insidePackage) { continue }
        Assert-Valid ($indexedPaths.Add($relativePath.Replace('\','/'))) "Duplicate layout path: $relativePath"
        Assert-Valid (Test-Path -LiteralPath $resolvedPath -PathType Leaf) "Missing indexed file: $relativePath"
        if (Test-Path -LiteralPath $resolvedPath -PathType Leaf) {
            $fileInfo = Get-Item -LiteralPath $resolvedPath
            Assert-Valid ($fileInfo.Length -eq [int64]$entry.size) "Stale layout size: $relativePath"
            $indexedBytes += $fileInfo.Length
        }
    }
    foreach ($fileInfo in Get-ChildItem -LiteralPath $packageRoot -Recurse -File) {
        if ($fileInfo.FullName -in @($manifestPath,$layoutPath)) { continue }
        $relativePath = [System.IO.Path]::GetRelativePath($packageRoot,$fileInfo.FullName).Replace('\','/')
        Assert-Valid ($indexedPaths.Contains($relativePath)) "File omitted from layout: $relativePath"
    }
    Assert-Valid ($manifest.total_package_size -eq $indexedBytes.ToString('D20')) 'manifest total_package_size does not match indexed content.'
    Write-Output ('Layout: {0} paths; {1} content bytes.' -f $indexedPaths.Count,$indexedBytes)

    $aircraftCfg = Read-Cfg (Join-Path $aircraftRoot 'aircraft.cfg')
    $fltsim = $aircraftCfg['FLTSIM.0']
    Assert-Valid ($aircraftCfg['VARIATION']['base_container'] -eq '..\FlyByWire_A380_842') 'Unexpected base_container.'
    $resolvedBase = Resolve-VfsReference $aircraftName $aircraftCfg['VARIATION']['base_container']
    Assert-Valid (Test-Path -LiteralPath (Join-Path $resolvedBase 'aircraft.cfg') -PathType Leaf) 'The referenced non-modular Stable base container is absent.'
    Assert-Valid ($fltsim['texture'] -eq 'AIRCHINA') 'aircraft.cfg texture must select AIRCHINA.'
    Assert-Valid ($fltsim['model'] -eq 'AIRCHINA') 'aircraft.cfg model must select AIRCHINA.'
    Assert-Valid ($fltsim['panel'] -eq '' -and $fltsim['sound'] -eq '') 'Panel and sound must inherit from the base aircraft.'
    Assert-Valid ($fltsim['atc_id'] -eq 'B-38AC') 'Unexpected fictional registration.'
    Assert-Valid ($fltsim['atc_id_enable'] -eq '0') 'Dynamic exterior registration must be disabled for the baked registration.'
    Assert-Valid ($fltsim['ui_createdby'] -eq 'FlyByWire Simulations') 'Aircraft grouping creator differs from the Stable base.'

    $modelCfg = Read-Cfg (Join-Path $aircraftRoot 'model.AIRCHINA\model.cfg')
    foreach ($modelKind in @('normal','interior')) {
        $modelReference = [string]$modelCfg['models'][$modelKind]
        $resolvedModel = Resolve-VfsReference "$aircraftName\model.AIRCHINA" $modelReference
        Assert-Valid ($resolvedModel.StartsWith($resolvedBase + '\',[System.StringComparison]::OrdinalIgnoreCase)) "Model reference leaves base container: $modelKind"
        Assert-Valid (Test-Path -LiteralPath $resolvedModel -PathType Leaf) "Missing inherited model XML: $resolvedModel"
    }
    $textureCfg = Read-Cfg (Join-Path $textureRoot 'texture.cfg')
    $resolvedTextureFallback = Resolve-VfsReference "$aircraftName\texture.AIRCHINA" $textureCfg['fltsim']['fallback.1']
    Assert-Valid ($resolvedTextureFallback -eq (Join-Path $resolvedBase 'texture')) 'Unexpected base texture fallback.'
    Assert-Valid (Test-Path -LiteralPath $resolvedTextureFallback -PathType Container) 'Base texture fallback directory is absent.'
    $baseManifest = [System.IO.File]::ReadAllText((Join-Path $baseRoot 'manifest.json')) | ConvertFrom-Json
    Assert-Valid ([string]$baseManifest.package_version -match '^2024\.1\.0(?:-|$)') ('Installed base differs from inspected Stable 2024.1.0: ' + $baseManifest.package_version)
    Write-Output ('Base: {0}; container/model/texture references resolved.' -f $baseManifest.package_version)

    $expectedTextures = [ordered]@{
        'A380X_FUSE1_ALBEDO.PNG.DDS' = 4096
        'A380X_FUSE2_ALBEDO.PNG.DDS' = 4096
        'A380X_FUSE3_ALBEDO.PNG.DDS' = 4096
        'A380X_FUSE4_ALBEDO.PNG.DDS' = 4096
        'A380X_FUSE5_ALBEDO.PNG.DDS' = 4096
        'A380_EXTERIOR_ENG_LH_ALBEDO.PNG.DDS' = 4096
        'A380_EXTERIOR_ENG_RH_ALBEDO.PNG.DDS' = 4096
        'A380X_REGISTRATION_ALBEDO.PNG.DDS' = 1024
        'A380X_EXTERIOR_WINGFENCE_ALBEDO.PNG.DDS' = 1024
    }
    foreach ($textureName in $expectedTextures.Keys) {
        Assert-Valid (Test-Path -LiteralPath (Join-Path $textureRoot $textureName) -PathType Leaf) "Required painted DDS is missing: $textureName"
    }
    foreach ($ddsInfo in Get-ChildItem -LiteralPath $textureRoot -File -Filter '*.dds') {
        $descriptorPath = $ddsInfo.FullName + '.json'
        Assert-Valid (Test-Path -LiteralPath $descriptorPath -PathType Leaf) "Missing MSFS DDS descriptor: $($ddsInfo.Name).json"
        if (Test-Path -LiteralPath $descriptorPath -PathType Leaf) {
            $descriptor = [System.IO.File]::ReadAllText($descriptorPath) | ConvertFrom-Json
            Assert-Valid ($descriptor.Version -eq 2) "Unexpected descriptor version: $($ddsInfo.Name)"
            Assert-Valid ([int64]$descriptor.SourceFileDate -gt 0) "Invalid source date in descriptor: $($ddsInfo.Name)"
            Assert-Valid ('FL_BITMAP_COMPRESSION' -in @($descriptor.Flags)) "Descriptor missing compression flag: $($ddsInfo.Name)"
            Assert-Valid ('FL_BITMAP_MIPMAP' -in @($descriptor.Flags)) "Descriptor missing mipmap flag: $($ddsInfo.Name)"
            if ($ddsInfo.Name -ieq 'A380X_REGISTRATION_ALBEDO.PNG.DDS') {
                Assert-Valid ($descriptor.HasTransp -eq $true) 'The cockpit registration descriptor must preserve transparency.'
            }
            $descriptorRelative = [System.IO.Path]::GetRelativePath($packageRoot,$descriptorPath).Replace('\','/')
            Assert-Valid ($indexedPaths.Contains($descriptorRelative)) "DDS descriptor omitted from layout: $descriptorRelative"
        }
        $header = New-Object byte[] 148
        $reader = [System.IO.File]::OpenRead($ddsInfo.FullName)
        try { $bytesRead = $reader.Read($header,0,148) } finally { $reader.Dispose() }
        Assert-Valid ($bytesRead -ge 128) "Truncated DDS header: $($ddsInfo.Name)"
        if ($bytesRead -lt 128) { continue }
        Assert-Valid ([System.Text.Encoding]::ASCII.GetString($header,0,4) -eq 'DDS ') "Invalid DDS magic: $($ddsInfo.Name)"
        Assert-Valid ([BitConverter]::ToUInt32($header,4) -eq 124) "Invalid DDS header size: $($ddsInfo.Name)"
        Assert-Valid ([BitConverter]::ToUInt32($header,76) -eq 32) "Invalid DDS pixel-format size: $($ddsInfo.Name)"
        $width = [BitConverter]::ToUInt32($header,16)
        $height = [BitConverter]::ToUInt32($header,12)
        $mips = [BitConverter]::ToUInt32($header,28)
        $fourCC = [System.Text.Encoding]::ASCII.GetString($header,84,4)
        if ($expectedTextures.Contains($ddsInfo.Name)) {
            Assert-Valid ($width -eq $expectedTextures[$ddsInfo.Name] -and $height -eq $expectedTextures[$ddsInfo.Name]) "Unexpected dimensions: $($ddsInfo.Name) is $width x $height"
        } else {
            $validationWarnings.Add("DDS is not in the planned nine-texture set: $($ddsInfo.Name)")
        }
        $validDimensions = ($width -gt 0 -and $height -gt 0 -and $width -le 16384 -and $height -le 16384)
        Assert-Valid $validDimensions "Unsupported DDS dimensions: $($ddsInfo.Name)"
        if (-not $validDimensions) { continue }
        $expectedMips = 1 + [int][Math]::Floor([Math]::Log2([Math]::Max($width,$height)))
        Assert-Valid ($mips -eq $expectedMips) "Incomplete mipmap chain: $($ddsInfo.Name) has $mips, expected $expectedMips"
        [int]$headerBytes = 128
        $format = $fourCC
        $supportedFormat = ($fourCC -eq 'DXT5')
        if ($fourCC -eq 'DX10') {
            $headerBytes = 148
            Assert-Valid ($bytesRead -eq 148) "Truncated DDS DX10 header: $($ddsInfo.Name)"
            $dxgi = [BitConverter]::ToUInt32($header,128)
            $format = 'DXGI ' + $dxgi
            $supportedFormat = ($dxgi -in @(77,78,98,99))
            Assert-Valid ([BitConverter]::ToUInt32($header,140) -eq 1) "DDS must have a single texture, not an array: $($ddsInfo.Name)"
        }
        Assert-Valid $supportedFormat "Expected BC3/DXT5 or BC7 RGBA compression: $($ddsInfo.Name) uses $format"
        if ($supportedFormat -and $mips -ge 1 -and $mips -le $expectedMips) {
            [int64]$minimumBytes = $headerBytes
            [int64]$mipWidth = $width
            [int64]$mipHeight = $height
            for ($level=0; $level -lt $mips; $level++) {
                $minimumBytes += [int64]([Math]::Max(1,[Math]::Ceiling($mipWidth/4.0)) * [Math]::Max(1,[Math]::Ceiling($mipHeight/4.0)) * 16)
                $mipWidth = [Math]::Max(1,[Math]::Floor($mipWidth/2.0))
                $mipHeight = [Math]::Max(1,[Math]::Floor($mipHeight/2.0))
            }
            Assert-Valid ($ddsInfo.Length -ge $minimumBytes) "DDS payload is shorter than its declared mip levels: $($ddsInfo.Name)"
        }
        Write-Output ('DDS: {0}; {1}x{2}; {3}; {4} mips.' -f $ddsInfo.Name,$width,$height,$format,$mips)
    }
} catch {
    $validationErrors.Add($_.Exception.Message)
}

foreach ($message in $validationWarnings) { Write-Warning $message }
if ($validationErrors.Count -gt 0) {
    foreach ($message in $validationErrors) { Write-Output ('FAIL: ' + $message) }
    throw ('Read-only package validation failed with {0} issue(s).' -f $validationErrors.Count)
}
Write-Output 'PASS: package metadata, DDS structure and installed base references are consistent.'
Write-Output 'This does not verify artwork alignment, alpha pixels, UI discovery or in-simulator rendering.'

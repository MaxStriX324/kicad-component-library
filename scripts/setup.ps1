param(
    [ValidateSet('Install', 'Update', 'Check')]
    [string]$Mode = 'Install',
    [string]$InstallDir = '',
    [string]$ConfigRoot = '',
    [switch]$NoUserEnv,
    [switch]$NonInteractive
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

$RepoUrl = 'https://github.com/MaxStriX324/kicad-component-library.git'
$ArchiveUrl = 'https://github.com/MaxStriX324/kicad-component-library/archive/refs/heads/main.zip'
$LibraryName = 'MaxStriX324'
$EnvName = 'MAXSTRIX_KICAD_LIB'

if (-not $InstallDir) {
    if (-not $env:LOCALAPPDATA) { throw 'LOCALAPPDATA is missing. Windows is required.' }
    $InstallDir = Join-Path $env:LOCALAPPDATA 'MaxStriX324\KiCadLibrary'
}
if (-not $ConfigRoot) {
    if ($env:KICAD_CONFIG_HOME) {
        $ConfigRoot = $env:KICAD_CONFIG_HOME
    } else {
        $ConfigRoot = Join-Path $env:APPDATA 'kicad'
    }
}
$InstallDir = [IO.Path]::GetFullPath($InstallDir)
$ConfigRoot = [IO.Path]::GetFullPath($ConfigRoot)

function Test-Library([string]$Root) {
    $required = @(
        'MaxStriX324.kicad_sym',
        'MaxStriX324.pretty\EC3503_16P_THT.kicad_mod',
        'MaxStriX324.pretty\UCC21750_SOIC16W_P1.27mm.kicad_mod',
        'MaxStriX324.3dshapes\EC3503_16P_THT.step',
        'MaxStriX324.3dshapes\UCC21750_SOIC16W_P1.27mm.step'
    )
    foreach ($rel in $required) {
        if (-not (Test-Path -LiteralPath (Join-Path $Root $rel) -PathType Leaf)) {
            throw "Missing library file: $rel"
        }
    }
}

function Assert-KiCadClosed {
    # KiCad can write the global library tables while closing. Never kill the
    # process automatically, since that can destroy unsaved schematic/PCB edits.
    while ($true) {
        $running = @(Get-Process -Name kicad,eeschema,pcbnew,cvpcb -ErrorAction SilentlyContinue)
        if ($running.Count -eq 0) { return }

        $processNames = (($running | Select-Object -ExpandProperty ProcessName -Unique) -join ', ')
        Write-Host ''
        Write-Host "KiCad is still running: $processNames" -ForegroundColor Yellow
        Write-Host 'Save your projects and close all KiCad, Schematic Editor and PCB Editor windows.'
        Write-Host 'The installer will continue in the SAME window without restarting the BAT file.'

        if ($NonInteractive) {
            throw 'KiCad is running in non-interactive mode. Close it and retry.'
        }
        try {
            $choice = Read-Host 'After closing KiCad press Enter to continue, or type Q to cancel'
        } catch {
            throw 'No interactive console is available. Close KiCad and rerun setup.bat.'
        }
        if ($choice -match '^[Qq]

function Get-KiCadConfigDirs {
    if (-not (Test-Path -LiteralPath $ConfigRoot -PathType Container)) {
        throw "KiCad configuration not found: $ConfigRoot. Launch KiCad and initialize default libraries once."
    }

    $locations = @()
    if ((Test-Path (Join-Path $ConfigRoot 'sym-lib-table')) -and
        (Test-Path (Join-Path $ConfigRoot 'fp-lib-table'))) {
        $locations += $ConfigRoot
    }

    $versionDirs = @(Get-ChildItem -LiteralPath $ConfigRoot -Directory -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match '^\d+\.\d+$' } |
        Sort-Object { [version]$_.Name } -Descending)

    foreach ($folder in $versionDirs) {
        if ([version]$folder.Name -lt [version]'8.0') { continue }
        $sym = Join-Path $folder.FullName 'sym-lib-table'
        $fp = Join-Path $folder.FullName 'fp-lib-table'
        if ((Test-Path -LiteralPath $sym -PathType Leaf) -and
            (Test-Path -LiteralPath $fp -PathType Leaf)) {
            $locations += $folder.FullName
        } else {
            Write-Warning "Skipping $($folder.Name): launch KiCad and initialize both global library tables first."
        }
    }
    if ($locations.Count -eq 0) {
        throw "No initialized KiCad 8/9/10 library tables found in $ConfigRoot. Start KiCad once, choose default libraries, close KiCad, then retry."
    }
    return $locations
}

function Find-LibraryEntry([string]$TableText) {
    $pattern = '\(\s*lib\s*\(\s*name\s+"MaxStriX324"\s*\)'
    $match = [regex]::Match($TableText, $pattern)
    if (-not $match.Success) { return $null }

    $depth = 0
    $quoted = $false
    $escaped = $false
    for ($i = $match.Index; $i -lt $TableText.Length; $i++) {
        $ch = $TableText[$i]
        if ($quoted) {
            if ($escaped) { $escaped = $false; continue }
            if ($ch -eq '\') { $escaped = $true; continue }
            if ($ch -eq '"') { $quoted = $false }
            continue
        }
        if ($ch -eq '"') { $quoted = $true; continue }
        if ($ch -eq '(') { $depth++ }
        if ($ch -eq ')') {
            $depth--
            if ($depth -eq 0) {
                return @{ Start = $match.Index; Length = $i - $match.Index + 1 }
            }
        }
    }
    throw 'Malformed existing MaxStriX324 library entry.'
}

function Register-Library([string]$TablePath, [string]$Kind, [string]$Uri) {
    $content = [IO.File]::ReadAllText($TablePath)
    $expectedHeader = if ($Kind -eq 'symbol') { 'sym_lib_table' } else { 'fp_lib_table' }
    if ($content -notmatch ('^\s*\(\s*' + $expectedHeader + '\b')) {
        throw "Unrecognized KiCad library table: $TablePath"
    }

    $targetUri = '$' + '{' + $EnvName + '}' + '/' + $Uri
    $entry = '(lib (name "' + $LibraryName + '")(type "KiCad")(uri "' +
             $targetUri + '")(options "")(descr "MaxStriX324 GitHub library"))'
    $location = Find-LibraryEntry $content
    if ($null -eq $location) {
        $at = $content.LastIndexOf(')')
        if ($at -lt 0) { throw "Invalid table: $TablePath" }
        $newText = $content.Insert($at, "  $entry" + [Environment]::NewLine)
    } else {
        $newText = $content.Remove($location.Start, $location.Length).Insert($location.Start, $entry)
    }

    if ($newText -ceq $content) {
        Write-Host "Already registered: $TablePath"
        return
    }
    $backup = $TablePath + '.bak.' + (Get-Date -Format 'yyyyMMdd_HHmmss_fff')
    Copy-Item -LiteralPath $TablePath -Destination $backup -ErrorAction Stop
    $utf8 = New-Object System.Text.UTF8Encoding($false)
    [IO.File]::WriteAllText($TablePath, $newText, $utf8)
    Write-Host "Registered: $TablePath"
    Write-Host "Backup: $backup"
}

function Download-Source([string]$Staging) {
    $git = Get-Command git -ErrorAction SilentlyContinue
    if ($git) {
        Write-Host 'Git detected. Cloning from GitHub...'
        & git clone --depth 1 --branch main $RepoUrl $Staging
        if ($LASTEXITCODE -ne 0) { throw 'git clone failed.' }
        return
    }

    Write-Host 'Git not installed. Downloading the public ZIP from GitHub...'
    [Net.ServicePointManager]::SecurityProtocol =
        [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
    $tmp = Join-Path ([IO.Path]::GetTempPath()) ('MaxStriX324-zip-' + [guid]::NewGuid().ToString('N'))
    try {
        New-Item -ItemType Directory -Path $tmp -Force | Out-Null
        $zip = Join-Path $tmp 'main.zip'
        Invoke-WebRequest -Uri $ArchiveUrl -OutFile $zip -UseBasicParsing
        Expand-Archive -LiteralPath $zip -DestinationPath $tmp -Force
        $src = Join-Path $tmp 'kicad-component-library-main'
        if (-not (Test-Path -LiteralPath $src)) { throw 'Invalid archive directory.' }
        Move-Item -LiteralPath $src -Destination $Staging
    } finally {
        if (Test-Path $tmp) { Remove-Item -LiteralPath $tmp -Recurse -Force }
    }
}

function Update-Checkout {
    $git = Get-Command git -ErrorAction SilentlyContinue
    if ($git -and (Test-Path -LiteralPath (Join-Path $InstallDir '.git'))) {
        Write-Host 'Updating installed Git checkout...'
        $dirty = @(& git -C $InstallDir status --porcelain)
        if ($LASTEXITCODE -ne 0) { throw 'Cannot inspect the Git checkout.' }
        if ($dirty.Count -gt 0) {
            throw 'Local edits detected. Commit or back up changes before updating.'
        }
        & git -C $InstallDir pull --ff-only origin main
        if ($LASTEXITCODE -ne 0) { throw 'git pull failed; existing files were preserved.' }
        Test-Library $InstallDir
        return
    }

    $parent = Split-Path -Parent $InstallDir
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
    $stage = Join-Path $parent ('_MaxStriX324-stage-' + [guid]::NewGuid().ToString('N'))
    $backup = $null
    try {
        Download-Source $stage
        Test-Library $stage
        if (Test-Path -LiteralPath $InstallDir) {
            $backup = $InstallDir + '.backup.' + (Get-Date -Format 'yyyyMMdd_HHmmss_fff')
            Move-Item -LiteralPath $InstallDir -Destination $backup
        }
        try {
            Move-Item -LiteralPath $stage -Destination $InstallDir
        } catch {
            if ($backup -and -not (Test-Path -LiteralPath $InstallDir)) {
                Move-Item -LiteralPath $backup -Destination $InstallDir
            }
            throw
        }
        if ($backup) { Write-Host "Previous version saved in: $backup" }
    } finally {
        if (Test-Path -LiteralPath $stage) {
            Remove-Item -LiteralPath $stage -Recurse -Force
        }
    }
}

try {
    Write-Host "MaxStriX324 KiCad library | $Mode"
    Write-Host "Library directory: $InstallDir"

    if ($Mode -eq 'Check') {
        Test-Library $InstallDir
        $configs = @(Get-KiCadConfigDirs)
        foreach ($config in $configs) {
            foreach ($t in @('sym-lib-table','fp-lib-table')) {
                $tableText = [IO.File]::ReadAllText((Join-Path $config $t))
                if (-not (Find-LibraryEntry $tableText)) { throw "$t not registered in $config" }
            }
            Write-Host "OK: $config"
        }
        if (-not $NoUserEnv) {
            $saved = [Environment]::GetEnvironmentVariable($EnvName, 'User')
            if ($saved -ne $InstallDir) { throw "User variable $EnvName is missing or incorrect." }
        }
        Write-Host 'Installed library and KiCad table entries are present.'
        exit 0
    }

    Assert-KiCadClosed
    # Fail early if the user's KiCad has not initialized the stock library tables.
    $configs = @(Get-KiCadConfigDirs)
    Update-Checkout
    Test-Library $InstallDir

    if (-not $NoUserEnv) {
        [Environment]::SetEnvironmentVariable($EnvName, $InstallDir, 'User')
    }
    Set-Item -Path ("Env:" + $EnvName) -Value $InstallDir

    foreach ($config in $configs) {
        Write-Host "Configuring KiCad: $config"
        Register-Library (Join-Path $config 'sym-lib-table') 'symbol' 'MaxStriX324.kicad_sym'
        Register-Library (Join-Path $config 'fp-lib-table') 'footprint' 'MaxStriX324.pretty'
    }

    Write-Host ''
    Write-Host 'Success. Restart KiCad completely to reload symbols, footprints and 3D models.'
    Write-Host "Library nickname: $LibraryName"
    Write-Host "To update: $InstallDir\update.bat"
    exit 0
} catch {
    Write-Host ''
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
) {
            throw 'Installation canceled by the user. No library table changes were made.'
        }
    }
}

function Get-KiCadConfigDirs {
    if (-not (Test-Path -LiteralPath $ConfigRoot -PathType Container)) {
        throw "KiCad configuration not found: $ConfigRoot. Launch KiCad and initialize default libraries once."
    }

    $locations = @()
    if ((Test-Path (Join-Path $ConfigRoot 'sym-lib-table')) -and
        (Test-Path (Join-Path $ConfigRoot 'fp-lib-table'))) {
        $locations += $ConfigRoot
    }

    $versionDirs = @(Get-ChildItem -LiteralPath $ConfigRoot -Directory -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match '^\d+\.\d+$' } |
        Sort-Object { [version]$_.Name } -Descending)

    foreach ($folder in $versionDirs) {
        if ([version]$folder.Name -lt [version]'8.0') { continue }
        $sym = Join-Path $folder.FullName 'sym-lib-table'
        $fp = Join-Path $folder.FullName 'fp-lib-table'
        if ((Test-Path -LiteralPath $sym -PathType Leaf) -and
            (Test-Path -LiteralPath $fp -PathType Leaf)) {
            $locations += $folder.FullName
        } else {
            Write-Warning "Skipping $($folder.Name): launch KiCad and initialize both global library tables first."
        }
    }
    if ($locations.Count -eq 0) {
        throw "No initialized KiCad 8/9/10 library tables found in $ConfigRoot. Start KiCad once, choose default libraries, close KiCad, then retry."
    }
    return $locations
}

function Find-LibraryEntry([string]$TableText) {
    $pattern = '\(\s*lib\s*\(\s*name\s+"MaxStriX324"\s*\)'
    $match = [regex]::Match($TableText, $pattern)
    if (-not $match.Success) { return $null }

    $depth = 0
    $quoted = $false
    $escaped = $false
    for ($i = $match.Index; $i -lt $TableText.Length; $i++) {
        $ch = $TableText[$i]
        if ($quoted) {
            if ($escaped) { $escaped = $false; continue }
            if ($ch -eq '\') { $escaped = $true; continue }
            if ($ch -eq '"') { $quoted = $false }
            continue
        }
        if ($ch -eq '"') { $quoted = $true; continue }
        if ($ch -eq '(') { $depth++ }
        if ($ch -eq ')') {
            $depth--
            if ($depth -eq 0) {
                return @{ Start = $match.Index; Length = $i - $match.Index + 1 }
            }
        }
    }
    throw 'Malformed existing MaxStriX324 library entry.'
}

function Register-Library([string]$TablePath, [string]$Kind, [string]$Uri) {
    $content = [IO.File]::ReadAllText($TablePath)
    $expectedHeader = if ($Kind -eq 'symbol') { 'sym_lib_table' } else { 'fp_lib_table' }
    if ($content -notmatch ('^\s*\(\s*' + $expectedHeader + '\b')) {
        throw "Unrecognized KiCad library table: $TablePath"
    }

    $targetUri = '$' + '{' + $EnvName + '}' + '/' + $Uri
    $entry = '(lib (name "' + $LibraryName + '")(type "KiCad")(uri "' +
             $targetUri + '")(options "")(descr "MaxStriX324 GitHub library"))'
    $location = Find-LibraryEntry $content
    if ($null -eq $location) {
        $at = $content.LastIndexOf(')')
        if ($at -lt 0) { throw "Invalid table: $TablePath" }
        $newText = $content.Insert($at, "  $entry" + [Environment]::NewLine)
    } else {
        $newText = $content.Remove($location.Start, $location.Length).Insert($location.Start, $entry)
    }

    if ($newText -ceq $content) {
        Write-Host "Already registered: $TablePath"
        return
    }
    $backup = $TablePath + '.bak.' + (Get-Date -Format 'yyyyMMdd_HHmmss_fff')
    Copy-Item -LiteralPath $TablePath -Destination $backup -ErrorAction Stop
    $utf8 = New-Object System.Text.UTF8Encoding($false)
    [IO.File]::WriteAllText($TablePath, $newText, $utf8)
    Write-Host "Registered: $TablePath"
    Write-Host "Backup: $backup"
}

function Download-Source([string]$Staging) {
    $git = Get-Command git -ErrorAction SilentlyContinue
    if ($git) {
        Write-Host 'Git detected. Cloning from GitHub...'
        & git clone --depth 1 --branch main $RepoUrl $Staging
        if ($LASTEXITCODE -ne 0) { throw 'git clone failed.' }
        return
    }

    Write-Host 'Git not installed. Downloading the public ZIP from GitHub...'
    [Net.ServicePointManager]::SecurityProtocol =
        [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
    $tmp = Join-Path ([IO.Path]::GetTempPath()) ('MaxStriX324-zip-' + [guid]::NewGuid().ToString('N'))
    try {
        New-Item -ItemType Directory -Path $tmp -Force | Out-Null
        $zip = Join-Path $tmp 'main.zip'
        Invoke-WebRequest -Uri $ArchiveUrl -OutFile $zip -UseBasicParsing
        Expand-Archive -LiteralPath $zip -DestinationPath $tmp -Force
        $src = Join-Path $tmp 'kicad-component-library-main'
        if (-not (Test-Path -LiteralPath $src)) { throw 'Invalid archive directory.' }
        Move-Item -LiteralPath $src -Destination $Staging
    } finally {
        if (Test-Path $tmp) { Remove-Item -LiteralPath $tmp -Recurse -Force }
    }
}

function Update-Checkout {
    $git = Get-Command git -ErrorAction SilentlyContinue
    if ($git -and (Test-Path -LiteralPath (Join-Path $InstallDir '.git'))) {
        Write-Host 'Updating installed Git checkout...'
        $dirty = @(& git -C $InstallDir status --porcelain)
        if ($LASTEXITCODE -ne 0) { throw 'Cannot inspect the Git checkout.' }
        if ($dirty.Count -gt 0) {
            throw 'Local edits detected. Commit or back up changes before updating.'
        }
        & git -C $InstallDir pull --ff-only origin main
        if ($LASTEXITCODE -ne 0) { throw 'git pull failed; existing files were preserved.' }
        Test-Library $InstallDir
        return
    }

    $parent = Split-Path -Parent $InstallDir
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
    $stage = Join-Path $parent ('_MaxStriX324-stage-' + [guid]::NewGuid().ToString('N'))
    $backup = $null
    try {
        Download-Source $stage
        Test-Library $stage
        if (Test-Path -LiteralPath $InstallDir) {
            $backup = $InstallDir + '.backup.' + (Get-Date -Format 'yyyyMMdd_HHmmss_fff')
            Move-Item -LiteralPath $InstallDir -Destination $backup
        }
        try {
            Move-Item -LiteralPath $stage -Destination $InstallDir
        } catch {
            if ($backup -and -not (Test-Path -LiteralPath $InstallDir)) {
                Move-Item -LiteralPath $backup -Destination $InstallDir
            }
            throw
        }
        if ($backup) { Write-Host "Previous version saved in: $backup" }
    } finally {
        if (Test-Path -LiteralPath $stage) {
            Remove-Item -LiteralPath $stage -Recurse -Force
        }
    }
}

try {
    Write-Host "MaxStriX324 KiCad library | $Mode"
    Write-Host "Library directory: $InstallDir"

    if ($Mode -eq 'Check') {
        Test-Library $InstallDir
        $configs = @(Get-KiCadConfigDirs)
        foreach ($config in $configs) {
            foreach ($t in @('sym-lib-table','fp-lib-table')) {
                $tableText = [IO.File]::ReadAllText((Join-Path $config $t))
                if (-not (Find-LibraryEntry $tableText)) { throw "$t not registered in $config" }
            }
            Write-Host "OK: $config"
        }
        if (-not $NoUserEnv) {
            $saved = [Environment]::GetEnvironmentVariable($EnvName, 'User')
            if ($saved -ne $InstallDir) { throw "User variable $EnvName is missing or incorrect." }
        }
        Write-Host 'Installed library and KiCad table entries are present.'
        exit 0
    }

    Assert-KiCadClosed
    # Fail early if the user's KiCad has not initialized the stock library tables.
    $configs = @(Get-KiCadConfigDirs)
    Update-Checkout
    Test-Library $InstallDir

    if (-not $NoUserEnv) {
        [Environment]::SetEnvironmentVariable($EnvName, $InstallDir, 'User')
    }
    Set-Item -Path ("Env:" + $EnvName) -Value $InstallDir

    foreach ($config in $configs) {
        Write-Host "Configuring KiCad: $config"
        Register-Library (Join-Path $config 'sym-lib-table') 'symbol' 'MaxStriX324.kicad_sym'
        Register-Library (Join-Path $config 'fp-lib-table') 'footprint' 'MaxStriX324.pretty'
    }

    Write-Host ''
    Write-Host 'Success. Restart KiCad completely to reload symbols, footprints and 3D models.'
    Write-Host "Library nickname: $LibraryName"
    Write-Host "To update: $InstallDir\update.bat"
    exit 0
} catch {
    Write-Host ''
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

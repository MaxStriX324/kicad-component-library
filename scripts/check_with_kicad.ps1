$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$cli = Get-Command kicad-cli -ErrorAction SilentlyContinue
if (-not $cli) {
    $candidates = @()
    if ($env:ProgramFiles) {
        $candidates += (Join-Path $env:ProgramFiles 'KiCad\10.0\bin\kicad-cli.exe')
        $candidates += (Join-Path $env:ProgramFiles 'KiCad\9.0\bin\kicad-cli.exe')
        $candidates += (Join-Path $env:ProgramFiles 'KiCad\8.0\bin\kicad-cli.exe')
    }
    $cli = $candidates | Where-Object { Test-Path -LiteralPath $_ -PathType Leaf } | Select-Object -First 1
} else {
    $cli = $cli.Source
}
if (-not $cli) {
    throw 'kicad-cli was not found. Run this check on a machine with KiCad 8, 9 or 10 installed.'
}
$symbols = Join-Path $root 'MaxStriX324.kicad_sym'
$footprints = Join-Path $root 'MaxStriX324.pretty'
$out = Join-Path ([IO.Path]::GetTempPath()) ('MaxStriX324-KiCad-check-' + [guid]::NewGuid().ToString('N'))
try {
    New-Item -ItemType Directory -Path (Join-Path $out 'symbols') -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $out 'footprints') -Force | Out-Null
    Write-Host "KiCad CLI: $cli"
    & $cli sym export svg --output (Join-Path $out 'symbols') $symbols
    if ($LASTEXITCODE -ne 0) { throw 'Native KiCad symbol parser rejected the library.' }
    & $cli fp export svg --layers F.SilkS,F.Fab --output (Join-Path $out 'footprints') $footprints
    if ($LASTEXITCODE -ne 0) { throw 'Native KiCad footprint parser rejected the library.' }
    Write-Host 'PASS: KiCad loaded symbols and footprints successfully.'
} finally {
    if (Test-Path -LiteralPath $out) { Remove-Item -LiteralPath $out -Recurse -Force -ErrorAction SilentlyContinue }
}

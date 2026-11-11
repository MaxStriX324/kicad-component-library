$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
if (-not (Test-Path (Join-Path $repo 'MaxStriX324.kicad_sym'))) { throw 'Symbol library not found.' }
[Environment]::SetEnvironmentVariable('MAXSTRIX_KICAD_LIB',$repo,'User')
$env:MAXSTRIX_KICAD_LIB = $repo
$cfgs = @(Get-ChildItem (Join-Path $env:APPDATA 'kicad') -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -match '^\d+\.\d+$' } | Sort-Object { [version]$_.Name } -Descending)
if ($cfgs.Count -eq 0) { throw 'Launch KiCad once and retry.' }
$cfg=$cfgs[0].FullName
function RegisterLibrary([string]$file,[string]$entry) {
  if (-not (Test-Path $file)) { throw "Missing $file. Run KiCad once to create its global library tables." }
  $txt=[IO.File]::ReadAllText($file)
  if ($txt -match '\(name\s+"MaxStriX324"\)') { Write-Host "Already registered: $file"; return }
  $at=$txt.LastIndexOf(')')
  if ($at -lt 0) { throw "Invalid library table: $file" }
  Copy-Item $file "$file.bak" -Force
  $txt=$txt.Insert($at,"  $entry`r`n")
  [IO.File]::WriteAllText($file,$txt,(New-Object Text.UTF8Encoding($false)))
  Write-Host "Added MaxStriX324: $file"
}
RegisterLibrary (Join-Path $cfg 'sym-lib-table') '(lib (name "MaxStriX324")(type "KiCad")(uri "${MAXSTRIX_KICAD_LIB}/MaxStriX324.kicad_sym")(options "")(descr "MaxStriX324 symbols"))'
RegisterLibrary (Join-Path $cfg 'fp-lib-table') '(lib (name "MaxStriX324")(type "KiCad")(uri "${MAXSTRIX_KICAD_LIB}/MaxStriX324.pretty")(options "")(descr "MaxStriX324 footprints"))'
Write-Host 'Restart KiCad completely.'

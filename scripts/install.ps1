param()
$ErrorActionPreference = 'Stop'
& (Join-Path $PSScriptRoot 'setup.ps1') -Mode Install
exit $LASTEXITCODE

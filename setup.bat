@echo off
setlocal
set "MAXSTRIX_SETUP_TEMP=%TEMP%\MaxStriX324-KiCad-Setup-%RANDOM%-%RANDOM%.ps1"
set "MAXSTRIX_SETUP_MODE=Install"
if /I "%~1"=="update" set "MAXSTRIX_SETUP_MODE=Update"
if /I "%~1"=="check" set "MAXSTRIX_SETUP_MODE=Check"
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -UseBasicParsing -Uri 'https://raw.githubusercontent.com/MaxStriX324/kicad-component-library/main/scripts/setup.ps1' -OutFile $env:MAXSTRIX_SETUP_TEMP; & $env:MAXSTRIX_SETUP_TEMP -Mode $env:MAXSTRIX_SETUP_MODE; if (-not $?) { exit 1 }"
set "RESULT=%ERRORLEVEL%"
if exist "%MAXSTRIX_SETUP_TEMP%" del /q "%MAXSTRIX_SETUP_TEMP%" >nul 2>&1
echo.
if not "%RESULT%"=="0" echo Operation failed. See details above.
pause
exit /b %RESULT%

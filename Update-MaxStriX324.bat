@echo off
setlocal
rem Stable updater outside the managed KiCad library folder. No Git needed.
set "MAXSTRIX_PS=%TEMP%\MaxStriX324-updater-%RANDOM%-%RANDOM%.ps1"
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -UseBasicParsing -Uri 'https://raw.githubusercontent.com/MaxStriX324/kicad-component-library/main/scripts/setup.ps1' -OutFile $env:MAXSTRIX_PS; & $env:MAXSTRIX_PS -Mode Update; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }"
set "RESULT=%ERRORLEVEL%"
if exist "%MAXSTRIX_PS%" del /q "%MAXSTRIX_PS%" >nul 2>&1
echo.
if "%RESULT%"=="0" (echo KiCad library updated. Restart KiCad if it was open.) else (echo Update failed. See error above.)
pause
exit /b %RESULT%

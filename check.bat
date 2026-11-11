@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\setup.ps1" -Mode Check
set "RESULT=%ERRORLEVEL%"
echo.
pause
exit /b %RESULT%

@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\setup.ps1" -Mode Install
set "RESULT=%ERRORLEVEL%"
echo.
if not "%RESULT%"=="0" echo Installation failed. See the message above.
pause
exit /b %RESULT%

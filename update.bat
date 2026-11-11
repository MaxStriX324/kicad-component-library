@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\setup.ps1" -Mode Update
set "RESULT=%ERRORLEVEL%"
echo.
if not "%RESULT%"=="0" echo Update failed. See the message above.
pause
exit /b %RESULT%

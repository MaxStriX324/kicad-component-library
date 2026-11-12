@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\setup.ps1" -Mode Check
if errorlevel 1 goto failed
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\check_with_kicad.ps1"
if errorlevel 1 goto failed
echo.
echo PASS: library registration and native KiCad parser
pause
exit /b 0
:failed
echo.
echo ERROR: library validation failed. See details above.
pause
exit /b 1

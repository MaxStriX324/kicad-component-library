@echo off
setlocal
set "UPDATER=%LOCALAPPDATA%\MaxStriX324\Update-MaxStriX324.bat"
if not exist "%UPDATER%" (
  echo External updater is missing. Run the latest setup.bat once to create it.
  pause
  exit /b 2
)
rem Run outside the managed library folder so it can be safely replaced.
start "MaxStriX324 KiCad Library Update" "%UPDATER%"
exit /b 0

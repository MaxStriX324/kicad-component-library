@echo off
setlocal
rem Update from GitHub with or without Git for Windows.
rem The updater must run outside the managed directory so ZIP installs can be replaced.
set "MANAGED_LIBRARY=%LOCALAPPDATA%\MaxStriX324\KiCadLibrary"
set "SETUP_BAT=%~dp0setup.bat"
if not exist "%SETUP_BAT%" (
  echo ERROR: setup.bat is missing next to update.bat.
  echo Get the current installer from https://github.com/MaxStriX324/kicad-component-library
  pause
  exit /b 2
)
cd /d "%TEMP%"
call "%SETUP_BAT%" update
exit /b %ERRORLEVEL%

@echo off
setlocal
where git >nul 2>&1 || (echo Git not installed.& pause & exit /b 1)
if not exist "%~dp0.git" (echo Clone the repository first.& pause & exit /b 2)
git -C "%~dp0" pull --ff-only
pause

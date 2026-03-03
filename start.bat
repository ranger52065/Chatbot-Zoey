@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo [ERROR] .venv not found. Please create venv and install requirements.
  pause
  exit /b 1
)

".venv\Scripts\python.exe" "Zoey\Zoey.py"

pause
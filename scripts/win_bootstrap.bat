@echo off
setlocal
rem Create .venv with Python 3.13 and install deps
py -3.13 -V >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
  echo [!] Python 3.13 not found by launcher. Install from python.org, or ensure 'py -3.13' works.
  exit /b 1
)
py -3.13 -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip wheel
python -m pip install -r requirements.txt
echo [OK] Environment ready.
echo To run: call .venv\Scripts\activate ^&^& python -m dcl_editor.app

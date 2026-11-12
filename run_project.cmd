@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\activate.bat" (
  echo Virtual environment not found. Run setup_and_run.cmd first.
  pause
  exit /b 1
)
call ".venv\Scripts\activate.bat"
python manage.py check
if errorlevel 1 pause
python manage.py runserver
endlocal

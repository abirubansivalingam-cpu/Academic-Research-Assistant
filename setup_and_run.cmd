@echo off
setlocal
cd /d "%~dp0"
echo ================================================
echo Academic Research Assistant - Setup
echo ================================================
where py >nul 2>nul
if errorlevel 1 (
  echo Python Launcher "py" was not found. Install Python and try again.
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment...
  py -m venv .venv
  if errorlevel 1 goto :error
)
call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
if errorlevel 1 goto :error
pip install -r requirements.txt
if errorlevel 1 goto :error
python manage.py check
if errorlevel 1 goto :error
python manage.py migrate
if errorlevel 1 goto :error
echo.
echo Setup complete. Starting the development server...
python manage.py runserver
goto :end
:error
echo.
echo Setup failed. Read the error above and check README.md.
pause
exit /b 1
:end
endlocal

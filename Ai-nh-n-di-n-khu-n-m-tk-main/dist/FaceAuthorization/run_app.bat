@echo off
REM Face Authorization System Launcher
REM This script launches the Flask application with embedded Python

setlocal enabledelayedexpansion

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Set Python to use the system installation
REM Update this path if needed
set PYTHON_EXE=python.exe
set FLASK_APP=app.py
set FLASK_ENV=production

REM Create necessary directories
if not exist uploads mkdir uploads
if not exist results mkdir results
if not exist logs mkdir logs
if not exist data mkdir data
if not exist index mkdir index

REM Set environment variables
set PYTHONUNBUFFERED=1
set FLASK_APP=%FLASK_APP%

REM Check if dependencies are installed
echo Checking dependencies...
%PYTHON_EXE% -c "import flask, cv2, insightface" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    %PYTHON_EXE% -m pip install -r requirements.txt
)

REM Start the application
echo.
echo Starting Face Authorization System...
echo Application will be available at http://localhost:5000
echo.
%PYTHON_EXE% -m flask run --host=0.0.0.0 --port=5000

pause

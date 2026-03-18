@echo off
REM Smart Parking Management System Launcher
REM Entry point: login.py

setlocal enabledelayedexpansion

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Navigate to smart-parking folder
cd smart-parking-management-system

REM Set Python to use the system installation
set PYTHON_EXE=python.exe

REM Create necessary directories
if not exist result mkdir result
if not exist result\face mkdir result\face
if not exist result\plate mkdir result\plate
if not exist result\fullface mkdir result\fullface

REM Set environment variables
set PYTHONUNBUFFERED=1

REM Check and install dependencies
echo Checking/Installing dependencies...
%PYTHON_EXE% -m pip install -q -r requirements.txt

REM Start the application
echo.
echo Starting Smart Parking Management System...
echo.
%PYTHON_EXE% login.py

pause

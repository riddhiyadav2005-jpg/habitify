@echo off
title Habitify - Habit Tracker Server
echo ===================================================
echo           Starting Habitify Web App
echo ===================================================
echo.
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.10+ from python.org
    pause
    exit /b
)

echo [1/2] Checking dependencies...
python -m pip install -r requirements.txt --quiet

echo [2/2] Starting Habitify Server on http://localhost:5000 ...
echo.
echo ===================================================
echo Open your browser at: http://localhost:5000
echo Press CTRL + C to stop the server
echo ===================================================
echo.
python app.py
pause

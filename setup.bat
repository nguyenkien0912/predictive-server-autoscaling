@echo off
echo ========================================
echo Predictive Server Autoscaling - Setup
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

REM Check Node.js installation
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo [OK] Python found: 
python --version

echo [OK] Node.js found: 
node --version

echo.
echo ========================================
echo Installing Backend Dependencies
echo ========================================
cd backend
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install backend dependencies
    pause
    exit /b 1
)
cd ..

echo.
echo ========================================
echo Installing Frontend Dependencies
echo ========================================
cd frontend
call npm install
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install frontend dependencies
    pause
    exit /b 1
)
cd ..

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the system:
echo   1. Open Terminal 1 and run: cd backend ^&^& python app.py
echo   2. Open Terminal 2 and run: cd frontend ^&^& npm run dev
echo.
pause

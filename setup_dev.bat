@echo off
REM Development Environment Setup Script for CIM Wizard Integrated (Windows)
REM This script sets up the local development environment

echo.
echo ===================================================
echo   CIM Wizard Integrated - Development Setup
echo ===================================================
echo.

REM Check Python installation
echo [1/7] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.10 or higher
    pause
    exit /b 1
)
echo [SUCCESS] Python is installed

REM Check Docker
echo [2/7] Checking Docker...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not installed or not running
    echo Please install and start Docker Desktop
    pause
    exit /b 1
)
echo [SUCCESS] Docker is available

REM Create virtual environment
echo [3/7] Creating Python virtual environment...
if not exist venv (
    python -m venv venv
    echo [SUCCESS] Virtual environment created
) else (
    echo [INFO] Virtual environment already exists
)

REM Activate virtual environment
echo [4/7] Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo [5/7] Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1

REM Install dependencies
echo [6/7] Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [SUCCESS] Dependencies installed

REM Create environment file
echo [7/7] Setting up environment configuration...
if not exist .env (
    copy .env.development .env >nul
    echo [SUCCESS] Development environment file created
) else (
    echo [INFO] Environment file already exists
    echo [INFO] To reset, delete .env and run this script again
)

echo.
echo ===================================================
echo   Development Setup Complete!
echo ===================================================
echo.
echo Next steps:
echo 1. Start PostGIS database:
echo    docker-compose up -d
echo.
echo 2. Initialize database (first time only):
echo    python scripts/populate_sample_data.py
echo.
echo 3. Run the application:
echo    python run.py
echo.
echo 4. Access the application:
echo    - API: http://localhost:8000
echo    - Docs: http://localhost:8000/docs
echo    - pgAdmin: http://localhost:5050 (if enabled)
echo.
echo To activate the virtual environment manually:
echo    venv\Scripts\activate.bat
echo.

pause
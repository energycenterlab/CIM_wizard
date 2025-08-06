@echo off
REM Docker PostGIS Setup Script for CIM Wizard Integrated (Windows)
REM This script automates the complete Docker PostGIS setup

echo 🐳 CIM Wizard Integrated - Docker PostGIS Setup (Windows)
echo ================================================

REM Check if Docker is running
echo [INFO] Checking Docker...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not running. Please start Docker first.
    pause
    exit /b 1
)
echo [SUCCESS] Docker is running

REM Check if docker-compose is available
echo [INFO] Checking Docker Compose...
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker Compose not found. Please install Docker Compose.
    pause
    exit /b 1
)
echo [SUCCESS] Docker Compose is available

REM Create .env file if it doesn't exist
if not exist .env (
    echo [INFO] Creating .env file...
    copy env.example .env >nul
    echo [SUCCESS] .env file created
) else (
    echo [INFO] .env file already exists
)

REM Stop existing containers
echo [INFO] Stopping existing containers...
docker-compose down >nul 2>&1

REM Build PostGIS container
echo [INFO] Building custom PostGIS container...
docker-compose build postgres
if %errorlevel% neq 0 (
    echo [ERROR] Failed to build PostGIS container
    pause
    exit /b 1
)
echo [SUCCESS] PostGIS container built

REM Start PostGIS container
echo [INFO] Starting PostGIS container...
docker-compose up postgres -d
if %errorlevel% neq 0 (
    echo [ERROR] Failed to start PostGIS container
    pause
    exit /b 1
)

REM Wait for container to be healthy
echo [INFO] Waiting for PostGIS to be ready...
set /a attempts=0
:wait_loop
set /a attempts+=1
if %attempts% gtr 30 (
    echo [ERROR] PostGIS container did not become healthy in time
    docker-compose logs postgres
    pause
    exit /b 1
)

docker-compose ps postgres | findstr "healthy" >nul
if %errorlevel% equ 0 (
    echo [SUCCESS] PostGIS container is healthy
    goto :continue
)

echo|set /p="."
timeout /t 2 /nobreak >nul
goto :wait_loop

:continue

REM Test database connection
echo [INFO] Testing database connection...
python scripts/test_docker_connection.py
if %errorlevel% neq 0 (
    echo [WARNING] Database connection test failed
    pause
)

REM Populate sample data
echo [INFO] Populating sample data...
python scripts/populate_sample_data.py
if %errorlevel% neq 0 (
    echo [WARNING] Sample data population failed
    pause
)

REM Start pgAdmin
echo [INFO] Starting pgAdmin...
docker-compose up pgadmin -d
echo [SUCCESS] pgAdmin started - access at http://localhost:5050
echo [INFO] pgAdmin credentials: admin@cimwizard.com / admin

REM Test application imports
echo [INFO] Testing application startup...
python -c "from app.db.database import engine; print('✅ Application can import database')" 2>nul
if %errorlevel% equ 0 (
    echo [SUCCESS] Application imports successful
) else (
    echo [WARNING] Application import test failed
)

echo.
echo [SUCCESS] 🎉 Docker PostGIS setup completed!
echo.
echo 📊 Service URLs:
echo    • Database: localhost:5432
echo    • pgAdmin: http://localhost:5050
echo    • Application: http://localhost:8000 (after starting)
echo.
echo 🚀 Next steps:
echo    1. Start the application: python run.py
echo    2. Test the API: python examples/simple_api_usage.py
echo    3. Access API docs: http://localhost:8000/docs
echo.
echo 🔧 Useful commands:
echo    • Check status: docker-compose ps
echo    • View logs: docker-compose logs postgres
echo    • Stop services: docker-compose down
echo    • Restart: docker-compose restart postgres
echo.
pause
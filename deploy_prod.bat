@echo off
REM Production Deployment Script for CIM Wizard Integrated (Windows)
REM This script deploys the application and database using Docker

echo.
echo ===================================================
echo   CIM Wizard Integrated - Production Deployment
echo ===================================================
echo.

REM Check if Docker is running
echo [1/7] Checking Docker...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)
echo [SUCCESS] Docker is running

REM Check if docker-compose is available
echo [2/7] Checking Docker Compose...
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker Compose not found. Please install Docker Compose.
    pause
    exit /b 1
)
echo [SUCCESS] Docker Compose is available

REM Create .env file if it doesn't exist
echo [3/7] Setting up environment...
if not exist .env (
    if exist .env.production (
        copy .env.production .env >nul
        echo [SUCCESS] Production environment file created
    ) else (
        echo [ERROR] .env.production file not found
        echo Please create .env.production with your production settings
        pause
        exit /b 1
    )
) else (
    echo [WARNING] Environment file already exists
    set /p overwrite="Overwrite with production settings? (y/N): "
    if /i "%overwrite%"=="y" (
        copy .env.production .env >nul
        echo [SUCCESS] Production environment applied
    ) else (
        echo [INFO] Using existing environment
    )
)

REM Stop existing containers
echo [4/7] Stopping existing containers...
docker-compose -f docker-compose.prod.yml down >nul 2>&1

REM Build containers
echo [5/7] Building containers...
docker-compose -f docker-compose.prod.yml build
if %errorlevel% neq 0 (
    echo [ERROR] Failed to build containers
    pause
    exit /b 1
)
echo [SUCCESS] Containers built

REM Start services
echo [6/7] Starting services...
docker-compose -f docker-compose.prod.yml up -d
if %errorlevel% neq 0 (
    echo [ERROR] Failed to start services
    pause
    exit /b 1
)
echo [SUCCESS] Services started

REM Wait for services to be healthy
echo [7/7] Waiting for services to be ready...
set /a attempts=0
:health_check
set /a attempts+=1
if %attempts% gtr 30 (
    echo [ERROR] Services did not become healthy in time
    docker-compose -f docker-compose.prod.yml logs
    pause
    exit /b 1
)

docker-compose -f docker-compose.prod.yml ps | findstr "healthy" >nul
if %errorlevel% neq 0 (
    echo|set /p="."
    timeout /t 2 /nobreak >nul
    goto :health_check
)

echo.
echo [SUCCESS] All services are healthy

REM Test application endpoint
echo.
echo Testing application endpoint...
timeout /t 5 /nobreak >nul
curl -f http://localhost:8000/docs >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Application is responding
) else (
    echo [WARNING] Application may still be starting up
    echo Please check http://localhost:8000/docs manually
)

echo.
echo ===================================================
echo   Production Deployment Complete!
echo ===================================================
echo.
echo Services Running:
echo   - Application:      http://localhost:8000
echo   - API Documentation: http://localhost:8000/docs
echo   - PostGIS Database: localhost:5432
echo.
echo To enable optional services:
echo   - pgAdmin:  docker-compose -f docker-compose.prod.yml --profile tools up pgadmin -d
echo   - Nginx:    docker-compose -f docker-compose.prod.yml --profile proxy up nginx -d
echo.
echo Management Commands:
echo   View logs:    docker-compose -f docker-compose.prod.yml logs -f
echo   Stop all:     docker-compose -f docker-compose.prod.yml down
echo   Restart all:  docker-compose -f docker-compose.prod.yml restart
echo   View status:  docker-compose -f docker-compose.prod.yml ps
echo.
echo Database Backup:
echo   docker exec cim_wizard_postgis_prod pg_dump -U cim_wizard_user cim_wizard_integrated > backup.sql
echo.
echo Database Restore:
echo   docker exec -i cim_wizard_postgis_prod psql -U cim_wizard_user cim_wizard_integrated < backup.sql
echo.

pause
@echo off
REM Docker PostGIS Setup Script for CIM Wizard Integrated (Windows)
REM This script sets up and starts the PostGIS database container

echo.
echo ===================================================
echo   CIM Wizard Integrated - PostGIS Docker Setup
echo ===================================================
echo.

REM Check if Docker is running
echo [1/6] Checking Docker...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)
echo [SUCCESS] Docker is running

REM Check if docker-compose is available
echo [2/6] Checking Docker Compose...
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker Compose not found. Please install Docker Compose.
    pause
    exit /b 1
)
echo [SUCCESS] Docker Compose is available

REM Create .env file if it doesn't exist
echo [3/6] Setting up environment...
if not exist .env (
    if exist .env.development (
        copy .env.development .env >nul
        echo [SUCCESS] Development environment file created
    ) else if exist .env.example (
        copy .env.example .env >nul
        echo [SUCCESS] Environment file created from example
    ) else (
        echo [WARNING] No environment template found
        echo [INFO] Please create .env file manually
    )
) else (
    echo [INFO] Environment file already exists
)

REM Stop existing containers
echo [4/6] Cleaning up existing containers...
docker-compose down >nul 2>&1

REM Build PostGIS container
echo [5/6] Building PostGIS container...
docker-compose build postgis
if %errorlevel% neq 0 (
    echo [ERROR] Failed to build PostGIS container
    pause
    exit /b 1
)
echo [SUCCESS] PostGIS container built

REM Start PostGIS container
echo [6/6] Starting PostGIS container...
docker-compose up postgis -d
if %errorlevel% neq 0 (
    echo [ERROR] Failed to start PostGIS container
    pause
    exit /b 1
)
echo [SUCCESS] PostGIS container started

REM Wait for database to be ready
echo.
echo Waiting for database to be ready...
set /a attempts=0
:wait_loop
set /a attempts+=1
if %attempts% gtr 30 (
    echo [ERROR] PostGIS container did not become healthy in time
    docker-compose logs postgis
    pause
    exit /b 1
)

docker-compose ps postgis | findstr "healthy" >nul
if %errorlevel% equ 0 (
    echo [SUCCESS] PostGIS is healthy
    goto :continue
)

echo|set /p="."
timeout /t 2 /nobreak >nul
goto :wait_loop

:continue

REM Test database connection
echo.
echo Testing database connection...
docker exec cim_wizard_postgis_dev pg_isready -U cim_wizard_user -d cim_wizard_integrated >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Database not ready, waiting...
    timeout /t 5 /nobreak >nul
    docker exec cim_wizard_postgis_dev pg_isready -U cim_wizard_user -d cim_wizard_integrated >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Database connection failed
        echo Please check Docker logs: docker-compose logs postgis
        pause
        exit /b 1
    )
)
echo [SUCCESS] Database connection successful

echo.
echo ===================================================
echo   PostGIS Setup Complete!
echo ===================================================
echo.
echo Database Connection Details:
echo   Host:     localhost
echo   Port:     5432
echo   Database: cim_wizard_integrated
echo   Username: cim_wizard_user
echo   Password: cim_wizard_password
echo.
echo Connection String:
echo   postgresql://cim_wizard_user:cim_wizard_password@localhost:5432/cim_wizard_integrated
echo.
echo Available Services:
echo   - PostgreSQL/PostGIS: localhost:5432
echo   - pgAdmin (optional): http://localhost:5050
echo     To enable: docker-compose --profile tools up pgadmin -d
echo.
echo Useful Commands:
echo   View logs:         docker-compose logs -f postgis
echo   Stop database:     docker-compose down
echo   Start database:    docker-compose up postgis -d
echo   Restart database:  docker-compose restart postgis
echo   Access psql:       docker exec -it cim_wizard_postgis_dev psql -U cim_wizard_user -d cim_wizard_integrated
echo.
echo Next Steps:
echo   1. Test connection:     python scripts/test_docker_connection.py
echo   2. Populate sample data: python scripts/populate_sample_data.py
echo   3. Run application:     python run.py
echo.

pause
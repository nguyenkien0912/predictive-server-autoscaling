@echo off
echo ========================================
echo  Predictive Server Autoscaling - Docker
echo ========================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed or not in PATH
    echo Please install Docker Desktop from https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo [INFO] Docker is installed
echo.

REM Check if Docker is running
docker ps >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running
    echo Please start Docker Desktop and try again
    pause
    exit /b 1
)

echo [INFO] Docker is running
echo.

REM Build and start containers
echo [INFO] Building and starting Docker containers...
echo This may take a few minutes on first run...
echo.

docker-compose up --build -d

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to start containers
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Containers started successfully!
echo ========================================
echo.
echo Backend API:    http://localhost:5000
echo Frontend UI:    http://localhost
echo.
echo To view logs:   docker-compose logs -f
echo To stop:        docker-compose stop
echo To remove:      docker-compose down
echo.

REM Wait a moment for services to start
timeout /t 3 >nul

REM Check container status
echo [INFO] Container status:
docker-compose ps

echo.
echo Opening browser in 3 seconds...
timeout /t 3 >nul
start http://localhost

pause

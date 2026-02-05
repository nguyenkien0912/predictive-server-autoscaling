@echo off
echo ========================================
echo  Stopping Docker Containers
echo ========================================
echo.

docker-compose down

if errorlevel 1 (
    echo [ERROR] Failed to stop containers
    pause
    exit /b 1
)

echo.
echo [INFO] All containers stopped and removed
echo.
pause

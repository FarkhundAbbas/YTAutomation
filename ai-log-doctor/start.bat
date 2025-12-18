@echo off
REM AI Log Doctor - Quick Start Script for Windows

echo ==========================================
echo  AI LOG DOCTOR - QUICK START
echo ==========================================
echo.

REM Check Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Docker is not installed!
    exit /b 1
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Docker Compose is not installed!
    exit /b 1
)

echo [OK] Docker and Docker Compose found
echo.

REM Start services
echo [STARTING] Starting services...
docker-compose up -d

echo [WAITING] Waiting for services to be healthy...
timeout /t 15 /nobreak >nul

REM Initialize database
echo [INIT] Initializing database...
docker-compose exec -T api-gateway python scripts/init_db.py

echo.
echo ==========================================
echo  SUCCESS! AI LOG DOCTOR IS READY
echo ==========================================
echo.
echo Frontend:  http://localhost:3000
echo API:       http://localhost:8000
echo API Docs:  http://localhost:8000/docs
echo.
echo Default Login:
echo   Username: admin
echo   Password: admin123
echo.
echo Run demo:
echo   python demo\run_demo.py
echo.
echo ==========================================

pause

@echo off
echo ============================================
echo   GetFit Frontend
echo ============================================
cd /d "%~dp0frontend"

REM Guard: ensure Node.js is installed
where node >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found. Install it from https://nodejs.org
    pause
    exit /b 1
)

REM Auto-install dependencies if node_modules is missing
if not exist "node_modules" (
    echo [INFO] node_modules not found — running npm install...
    npm install
    if errorlevel 1 (
        echo [ERROR] npm install failed.
        pause
        exit /b 1
    )
    echo.
)

echo [OK] Starting Vite dev server on http://localhost:5173
echo.

npm run dev
pause

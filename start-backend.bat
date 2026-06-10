@echo off
echo ============================================
echo   GetFit Backend
echo ============================================
cd /d "%~dp0backend"

REM Guard: ensure the virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found.
    echo.
    echo Run the following commands first:
    echo   cd backend
    echo   python -m venv venv
    echo   venv\Scripts\pip install -r requirements.txt
    echo   venv\Scripts\python seed_users.py
    pause
    exit /b 1
)

echo [OK] Using venv Python
echo [OK] Starting uvicorn on http://localhost:8000
echo [OK] Swagger docs at http://localhost:8000/docs
echo.

REM Always use the venv Python to avoid system-Python / package conflicts
venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pause

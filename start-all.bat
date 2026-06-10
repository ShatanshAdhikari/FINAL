@echo off
echo ============================================
echo   GetFit — Starting Backend + Frontend
echo ============================================
echo.

REM Launch backend in its own terminal window
start "GetFit Backend" cmd /k "%~dp0start-backend.bat"

REM Short delay so backend starts binding its port first
timeout /t 2 /nobreak >nul

REM Launch frontend in its own terminal window
start "GetFit Frontend" cmd /k "%~dp0start-frontend.bat"

echo.
echo   Backend  -^>  http://localhost:8000
echo   API docs -^>  http://localhost:8000/docs
echo   Frontend -^>  http://localhost:5173
echo.
echo Both services launched in separate windows.
echo Close those windows (or press Ctrl+C inside them) to stop.
pause

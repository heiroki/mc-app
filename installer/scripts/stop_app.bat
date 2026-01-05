@echo off
REM installer/scripts/stop_app.bat

echo ========================================
echo  MyOllamaApp Stopping...
echo ========================================
echo.

REM Flutter App停止
echo [1/2] Stopping Application...
taskkill /F /IM frontend.exe 2>nul
if %errorlevel%==0 (
    echo    ✅ Application stopped
) else (
    echo    ℹ️  Application was not running
)

echo.

REM Backend停止
echo [2/2] Stopping Backend...
taskkill /F /IM backend_server.exe 2>nul
if %errorlevel%==0 (
    echo    ✅ Backend stopped
) else (
    echo    ℹ️  Backend was not running
)

echo.
echo ========================================
echo  ✅ Stopped Successfully!
echo ========================================
echo.
timeout /t 2 /nobreak > nul

@echo off
REM installer/scripts/start_app.bat

REM カレントディレクトリをスクリプトの場所の親に移動
cd /d "%~dp0.."

echo ========================================
echo  MyOllamaApp Starting...
echo ========================================
echo.

REM Backend起動
echo [1/2] Starting Backend...
start /B "" backend\backend_server.exe
if %errorlevel% neq 0 (
    echo.
    echo ❌ Error: Failed to start Backend
    echo    Please check if backend_server.exe exists
    pause
    exit /b 1
)

echo    ✅ Backend started

REM 起動待機（3秒）
echo.
echo [Waiting 3 seconds for backend to initialize...]
timeout /t 3 /nobreak > nul

REM Flutter起動
echo.
echo [2/2] Starting Application...
start "" flutter_app\frontend.exe
if %errorlevel% neq 0 (
    echo.
    echo ❌ Error: Failed to start Application
    echo    Please check if frontend.exe exists
    pause
    exit /b 1
)

echo    ✅ Application started

echo.
echo ========================================
echo  ✅ Started Successfully!
echo ========================================
echo.
echo Press any key to close this window...
pause > nul

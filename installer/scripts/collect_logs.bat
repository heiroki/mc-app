@echo off
REM installer/scripts/collect_logs.bat

echo ========================================
echo  Log Collection Tool
echo ========================================
echo.

REM 出力先ディレクトリ作成（デスクトップ）
set OUTPUT_DIR=%USERPROFILE%\Desktop\MyOllamaApp_Logs_%DATE:~0,4%%DATE:~5,2%%DATE:~8,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%
set OUTPUT_DIR=%OUTPUT_DIR: =0%

echo Creating log directory...
mkdir "%OUTPUT_DIR%" 2>nul

REM ========================================
REM 1. アプリケーションログ
REM ========================================
echo.
echo [1/4] Collecting application logs...
if exist "%LOCALAPPDATA%\MyOllamaApp\logs\*" (
    xcopy /Y /I "%LOCALAPPDATA%\MyOllamaApp\logs\*" "%OUTPUT_DIR%\logs\"
    echo    ✅ Application logs copied
) else (
    echo    ℹ️  No application logs found
)

REM ========================================
REM 2. システム情報
REM ========================================
echo.
echo [2/4] Collecting system information...
systeminfo > "%OUTPUT_DIR%\systeminfo.txt" 2>nul
echo    ✅ System info saved

REM ========================================
REM 3. CPU情報
REM ========================================
echo.
echo [3/4] Collecting CPU information...
wmic cpu get name,numberofcores,numberoflogicalprocessors /format:table > "%OUTPUT_DIR%\cpuinfo.txt" 2>nul
echo    ✅ CPU info saved

REM ========================================
REM 4. メモリ情報
REM ========================================
echo.
echo [4/4] Collecting memory information...
wmic memorychip get capacity,speed,manufacturer /format:table > "%OUTPUT_DIR%\meminfo.txt" 2>nul
echo    ✅ Memory info saved

REM ========================================
REM 完了
REM ========================================
echo.
echo ========================================
echo  ✅ Log Collection Completed!
echo ========================================
echo.
echo Logs saved to:
echo %OUTPUT_DIR%
echo.
echo Please send this folder to support.
echo.
pause

@echo off
chcp 65001 >nul
setlocal EnableExtensions
cd /d "%~dp0..\platform"

if not exist "compose.yml" (
    echo [Lỗi] Không tìm thấy compose.yml. Thư mục: %CD%
    pause
    exit /b 1
)

echo.
echo === VellaIPTV — Dừng và gỡ container (docker compose down) ===
echo.

docker compose down
set "EC=%ERRORLEVEL%"
if not "%EC%"=="0" (
    echo.
    echo [Lỗi] docker compose down thoát với mã %EC%.
    pause
    exit /b %EC%
)

echo Đã tắt stack.
echo.
pause
endlocal

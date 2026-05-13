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
echo === VellaIPTV — Khởi động stack (docker compose watch) ===
echo    Frontend:  http://localhost:5173
echo    Backend:   http://localhost:8000
echo    API docs:  http://localhost:8000/docs
echo    Adminer:   http://localhost:8080
echo    Traefik:   http://localhost:8090
echo.
echo Nhấn Ctrl+C để dừng phiên này. Để tắt hẳn stack, chạy platform-stop.bat
echo.

docker compose watch
set "EC=%ERRORLEVEL%"
if not "%EC%"=="0" (
    echo.
    echo [Lỗi] docker compose watch thoát với mã %EC%.
    echo Kiểm tra Docker Desktop đã chạy và: docker compose version
    pause
    exit /b %EC%
)

endlocal

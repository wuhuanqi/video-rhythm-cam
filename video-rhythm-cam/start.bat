@echo off
REM Video Rhythm Cam - Windows 启动脚本

echo 🎬 Video Rhythm Cam - 启动中...
echo.

REM 检查依赖
echo 📋 检查依赖...

where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Node.js 未安装
    exit /b 1
)

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Python 未安装
    exit /b 1
)

where ffmpeg >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ FFmpeg 未安装
    exit /b 1
)

echo ✅ 所有依赖已安装
echo.

REM 创建必要的目录
if not exist uploads mkdir uploads
if not exist output mkdir output

REM 启动 Python API (新窗口)
echo 🚀 启动 Python API 服务...
start "Video Rhythm Cam API" python-api\api.py

REM 等待 API 启动
echo ⏳ 等待 Python API 启动...
timeout /t 3 /nobreak >nul

REM 启动 Web 应用
echo 🚀 启动 Web 应用...
echo.
echo ✅ 服务启动完成!
echo    - Python API: http://localhost:8000
echo    - Web 应用: http://localhost:3000
echo.

cd web
npm run dev

pause

@echo off
REM Video Rhythm Cam 宣传片快速启动脚本 (Windows)

setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
set REMOTION_DIR=%SCRIPT_DIR%remotion
set OUTPUT_DIR=%SCRIPT_DIR%output

REM 显示帮助信息
if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="--help" goto help
if "%1"=="-h" goto help

set COMMAND=%1

if "%COMMAND%"=="preview" goto preview
if "%COMMAND%"=="render" goto render
if "%COMMAND%"=="render-hq" goto render_hq
if "%COMMAND%"=="render-web" goto render_web
if "%COMMAND%"=="render-fast" goto render_fast

echo 未知命令: %COMMAND%
goto help

:preview
echo [INFO] 启动 Remotion Studio...
cd /d "%REMOTION_DIR%"
call npm start
goto end

:render
echo [INFO] 渲染宣传片...
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"
cd /d "%REMOTION_DIR%"
npx remotion render PromoVideo "%OUTPUT_DIR%\promo-video.mp4" --quality=90 --jpeg-quality=90 --codec=h264
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] 宣传片渲染完成！
    echo [INFO] 文件位置: %OUTPUT_DIR%\promo-video.mp4
) else (
    echo [ERROR] 渲染失败
)
goto end

:render_hq
echo [INFO] 渲染高质量宣传片...
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"
cd /d "%REMOTION_DIR%"
npx remotion render PromoVideo "%OUTPUT_DIR%\promo-video-hq.mp4" --quality=95 --jpeg-quality=95 --codec=h264
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] 宣传片渲染完成！
    echo [INFO] 文件位置: %OUTPUT_DIR%\promo-video-hq.mp4
) else (
    echo [ERROR] 渲染失败
)
goto end

:render_web
echo [INFO] 渲染网络版宣传片...
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"
cd /d "%REMOTION_DIR%"
npx remotion render PromoVideo "%OUTPUT_DIR%\promo-video-web.mp4" --quality=90 --jpeg-quality=90 --codec=h264
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] 宣传片渲染完成！
    echo [INFO] 文件位置: %OUTPUT_DIR%\promo-video-web.mp4
) else (
    echo [ERROR] 渲染失败
)
goto end

:render_fast
echo [INFO] 快速渲染宣传片...
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"
cd /d "%REMOTION_DIR%"
npx remotion render PromoVideo "%OUTPUT_DIR%\promo-video-fast.mp4" --quality=80 --jpeg-quality=80 --codec=h264
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] 宣传片渲染完成！
    echo [INFO] 文件位置: %OUTPUT_DIR%\promo-video-fast.mp4
) else (
    echo [ERROR] 渲染失败
)
goto end

:help
echo Video Rhythm Cam 宣传片工具
echo.
echo 用法: promo.bat [命令]
echo.
echo 命令:
echo   preview        启动 Remotion Studio 预览宣传片
echo   render         渲染宣传片为 MP4 视频
echo   render-hq      渲染高质量宣传片
echo   render-web     渲染适合网络发布的宣传片
echo   render-fast    快速渲染预览版
echo   help           显示此帮助信息
echo.
echo 示例:
echo   promo.bat preview        # 预览宣传片
echo   promo.bat render         # 渲染宣传片
echo   promo.bat render-hq      # 高质量渲染
echo.

:end
pause

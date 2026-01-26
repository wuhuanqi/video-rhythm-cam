#!/bin/bash

# Video Rhythm Cam - 启动脚本

set -e

echo "🎬 Video Rhythm Cam - 启动中..."
echo ""

# 检查依赖
echo "📋 检查依赖..."

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装"
    exit 1
fi

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 未安装"
    exit 1
fi

# 检查 FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ FFmpeg 未安装"
    exit 1
fi

echo "✅ 所有依赖已安装"
echo ""

# 创建必要的目录
mkdir -p uploads
mkdir -p output
mkdir -p python-api

# 启动 Python API (后台)
echo "🚀 启动 Python API 服务..."
cd python-api
python api.py &
API_PID=$!
cd ..

# 等待 API 启动
echo "⏳ 等待 Python API 启动..."
sleep 3

# 检查 API 是否启动成功
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Python API 已启动 (PID: $API_PID)"
else
    echo "❌ Python API 启动失败"
    exit 1
fi

echo ""

# 启动 Web 应用
echo "🚀 启动 Web 应用..."
cd web
npm run dev

# 清理: 当 Web 应用停止时，停止 Python API
trap "kill $API_PID" EXIT

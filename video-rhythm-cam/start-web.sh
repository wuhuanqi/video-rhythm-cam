#!/bin/bash

# Video Rhythm Cam Web 应用启动脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEB_DIR="$SCRIPT_DIR/web"
API_DIR="$SCRIPT_DIR/python-api"

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# 检查依赖
check_dependencies() {
    print_info "检查依赖..."

    if ! command -v node &> /dev/null; then
        print_error "Node.js 未安装"
        exit 1
    fi

    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 未安装"
        exit 1
    fi

    print_success "依赖检查完成"
}

# 启动 Python API
start_api() {
    print_info "启动 Python API 服务器..."

    cd "$API_DIR"
    python3 api.py &
    API_PID=$!

    # 等待 API 启动
    sleep 3

    if curl -s http://localhost:8000/docs > /dev/null; then
        print_success "Python API 已启动 (PID: $API_PID)"
        echo $API_PID > /tmp/video-rhythm-cam-api.pid
    else
        print_error "Python API 启动失败"
        exit 1
    fi
}

# 启动 Web 前端
start_web() {
    print_info "启动 Web 前端服务器..."

    cd "$WEB_DIR"
    npm run dev &
    WEB_PID=$!

    sleep 3

    print_success "Web 前端已启动 (PID: $WEB_PID)"
    echo $WEB_PID > /tmp/video-rhythm-cam-web.pid
}

# 主函数
main() {
    echo ""
    echo "🚀 Video Rhythm Cam Web 应用启动中..."
    echo ""

    check_dependencies
    start_api
    start_web

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    print_success "所有服务已启动！"
    echo ""
    echo -e "${GREEN}前端访问:${NC}  http://localhost:3000"
    echo -e "${GREEN}API 文档:${NC}  http://localhost:8000/docs"
    echo ""
    echo "按 Ctrl+C 停止所有服务"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # 等待用户中断
    wait
}

# 捕获退出信号
cleanup() {
    echo ""
    print_info "正在停止服务..."

    if [ -f /tmp/video-rhythm-cam-api.pid ]; then
        kill $(cat /tmp/video-rhythm-cam-api.pid) 2>/dev/null
        rm /tmp/video-rhythm-cam-api.pid
    fi

    if [ -f /tmp/video-rhythm-cam-web.pid ]; then
        kill $(cat /tmp/video-rhythm-cam-web.pid) 2>/dev/null
        rm /tmp/video-rhythm-cam-web.pid
    fi

    print_success "所有服务已停止"
    exit 0
}

trap cleanup SIGINT SIGTERM

main

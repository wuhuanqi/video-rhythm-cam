#!/bin/bash

# Video Rhythm Cam 宣传片快速启动脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REMOTION_DIR="$SCRIPT_DIR/remotion"
OUTPUT_DIR="$SCRIPT_DIR/output"

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# 显示帮助信息
show_help() {
    cat << EOF
Video Rhythm Cam 宣传片工具

用法: ./promo.sh [命令] [选项]

命令:
  preview        启动 Remotion Studio 预览宣传片
  render         渲染宣传片为 MP4 视频
  render-hq      渲染高质量宣传片
  render-web     渲染适合网络发布的宣传片
  render-fast    快速渲染预览版
  help           显示此帮助信息

渲染选项:
  --output PATH  指定输出文件路径 (默认: output/promo-video.mp4)
  --quality N    渲染质量 1-100 (默认: 90)

示例:
  ./promo.sh preview                    # 预览宣传片
  ./promo.sh render                     # 渲染宣传片
  ./promo.sh render --output custom.mp4 # 渲染到指定路径
  ./promo.sh render-hq                  # 高质量渲染

EOF
}

# 检查依赖
check_dependencies() {
    print_info "检查依赖..."

    if ! command -v node &> /dev/null; then
        print_error "Node.js 未安装，请先安装 Node.js"
        print_info "访问 https://nodejs.org/ 下载安装"
        exit 1
    fi

    if ! command -v npm &> /dev/null; then
        print_error "npm 未安装"
        exit 1
    fi

    if [ ! -d "$REMOTION_DIR/node_modules" ]; then
        print_warning "Remotion 依赖未安装，正在安装..."
        cd "$REMOTION_DIR"
        npm install --registry=https://registry.npmmirror.com
        cd "$SCRIPT_DIR"
        print_success "依赖安装完成"
    fi

    print_success "依赖检查完成"
}

# 预览宣传片
preview_promo() {
    check_dependencies

    print_info "启动 Remotion Studio..."

    cd "$REMOTION_DIR"
    npm start

    print_success "预览已关闭"
}

# 渲染宣传片
render_promo() {
    local quality=${1:-90}
    local output_path=${2:-"$OUTPUT_DIR/promo-video.mp4"}

    check_dependencies

    # 创建输出目录
    mkdir -p "$OUTPUT_DIR"

    print_info "渲染宣传片..."
    print_info "质量: $quality"
    print_info "输出: $output_path"

    cd "$REMOTION_DIR"

    npx remotion render PromoVideo "$output_path" \
        --quality="$quality" \
        --jpeg-quality="$quality" \
        --codec=h264

    if [ $? -eq 0 ]; then
        print_success "宣传片渲染完成！"
        print_info "文件位置: $output_path"

        # 获取文件大小
        if [ -f "$output_path" ]; then
            file_size=$(ls -lh "$output_path" | awk '{print $5}')
            print_info "文件大小: $file_size"
        fi
    else
        print_error "渲染失败"
        exit 1
    fi
}

# 主函数
main() {
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi

    local command=$1
    shift

    case $command in
        preview)
            preview_promo
            ;;
        render)
            render_promo 90 "$OUTPUT_DIR/promo-video.mp4"
            ;;
        render-hq)
            render_promo 95 "$OUTPUT_DIR/promo-video-hq.mp4"
            ;;
        render-web)
            render_promo 90 "$OUTPUT_DIR/promo-video-web.mp4"
            ;;
        render-fast)
            render_promo 80 "$OUTPUT_DIR/promo-video-fast.mp4"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "未知命令: $command"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"

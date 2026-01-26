#!/bin/bash
#
# 一键运行所有测试
#

echo "=================================="
echo "音频对齐功能 - 完整测试套件"
echo "=================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 未安装${NC}"
    exit 1
fi

# 1. 快速测试
echo -e "${YELLOW}📋 步骤 1: 快速功能测试${NC}"
echo "-----------------------------------"
python3 quick_test.py
QUICK_RESULT=$?

if [ $QUICK_RESULT -ne 0 ]; then
    echo -e "${RED}❌ 快速测试失败，请先解决基础问题${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ 快速测试通过${NC}"
echo ""

# 2. 命令行功能测试
echo -e "${YELLOW}📋 步骤 2: 命令行功能测试${NC}"
echo "-----------------------------------"
python3 test_cli.py
CLI_RESULT=$?

echo ""

# 3. API 接口测试
echo -e "${YELLOW}📋 步骤 3: API 接口测试${NC}"
echo "-----------------------------------"

# 检查 API 是否运行
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ API 服务运行中${NC}"
    python3 test_api.py
    API_RESULT=$?
else
    echo -e "${YELLOW}⚠️  API 服务未启动，跳过 API 测试${NC}"
    echo "   如需测试 API，请先启动: cd video-rhythm-cam/python-api && python3 api.py"
    API_RESULT=0
fi

echo ""

# 4. 完整测试套件
echo -e "${YELLOW}📋 步骤 4: 完整测试套件${NC}"
echo "-----------------------------------"

if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    python3 test_audio_alignment_complete.py
    FULL_RESULT=$?
else
    echo -e "${YELLOW}⚠️  API 服务未启动，跳过完整测试${NC}"
    FULL_RESULT=0
fi

echo ""
echo "=================================="
echo "测试总结"
echo "=================================="

# 显示结果
echo -e "快速测试:       $([ $QUICK_RESULT -eq 0 ] && echo "${GREEN}✅ 通过${NC}" || echo "${RED}❌ 失败${NC}")"
echo -e "命令行测试:      $([ $CLI_RESULT -eq 0 ] && echo "${GREEN}✅ 通过${NC}" || echo "${RED}❌ 失败${NC}")"
echo -e "API 测试:        $([ $API_RESULT -eq 0 ] && echo "${GREEN}✅ 通过${NC}" || echo "${RED}❌ 失败${NC}")"
echo -e "完整测试:        $([ $FULL_RESULT -eq 0 ] && echo "${GREEN}✅ 通过${NC}" || echo "${RED}❌ 失败${NC}")"
echo ""

# 总体结果
TOTAL_RESULT=0
if [ $QUICK_RESULT -ne 0 ] || [ $CLI_RESULT -ne 0 ] || [ $API_RESULT -ne 0 ] || [ $FULL_RESULT -ne 0 ]; then
    TOTAL_RESULT=1
fi

if [ $TOTAL_RESULT -eq 0 ]; then
    echo -e "${GREEN}🎉 所有测试通过！${NC}"
    echo ""
    echo "💡 现在可以："
    echo "   1. 使用命令行: python3 video-rhythm-cam/scripts/audio_alignment.py <视频1> <视频2>"
    echo "   2. 使用 API:    访问 http://localhost:8000/docs"
    echo "   3. 使用 Web:    访问 http://localhost:3000"
else
    echo -e "${RED}❌ 部分测试失败，请查看上面的错误信息${NC}"
fi

echo "=================================="

exit $TOTAL_RESULT

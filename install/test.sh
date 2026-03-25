#!/bin/bash
# 快速测试脚本 - 测试采集功能

set -e

SKILL_DIR="${SKILL_DIR:-$HOME/.agents/skills/douyin-shop-automation}"
CONFIG_FILE="$SKILL_DIR/config/config.json"

echo "================================"
echo "  抖音小店自动化上货 - 快速测试"
echo "================================"
echo ""

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[✓] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[!] $1${NC}"
}

error() {
    echo -e "${RED}[✗] $1${NC}"
}

# 检查环境
echo "【Step 1】检查环境..."

if [ ! -d "$SKILL_DIR" ]; then
    error "Skill未安装: $SKILL_DIR"
    exit 1
fi
log "Skill目录存在"

if [ ! -f "$CONFIG_FILE" ]; then
    error "配置文件不存在: $CONFIG_FILE"
    exit 1
fi
log "配置文件存在"

if command -v python3 &> /dev/null; then
    log "Python3: $(python3 --version)"
else
    error "未找到Python3"
    exit 1
fi

if python3 -c "import playwright" 2>/dev/null; then
    log "Playwright已安装"
else
    warn "Playwright未安装，运行: pip3 install playwright"
fi

echo ""
echo "【Step 2】测试采集功能..."

# 创建测试目录
mkdir -p "$SKILL_DIR/data/test"
TEST_OUTPUT="$SKILL_DIR/data/test/test_$(date +%Y%m%d_%H%M%S).json"

# 运行采集测试
python3 "$SKILL_DIR/lib/collector.py" \
    --keyword "测试" \
    --limit 3 \
    --output "$TEST_OUTPUT" \
    --config "$CONFIG_FILE" 2>&1 | tee /tmp/test_collect.log

if [ -f "$TEST_OUTPUT" ]; then
    COUNT=$(cat "$TEST_OUTPUT" | grep -c '"id"' || echo "0")
    if [ "$COUNT" -gt 0 ]; then
        log "采集测试成功！获取 $COUNT 个商品"
        echo "  数据文件: $TEST_OUTPUT"
    else
        warn "采集成功但未获取到商品数据"
        echo "  可能原因：WSY Token无效或网络问题"
        echo "  日志: /tmp/test_collect.log"
    fi
else
    error "采集测试失败"
    echo "  日志: /tmp/test_collect.log"
    exit 1
fi

echo ""
echo "【Step 3】测试数据处理..."

TEST_PROCESSED="$SKILL_DIR/data/test/processed_$(date +%Y%m%d_%H%M%S).json"

python3 "$SKILL_DIR/lib/processor.py" \
    --input "$TEST_OUTPUT" \
    --profit 30 \
    --output "$TEST_PROCESSED" \
    --config "$CONFIG_FILE" 2>&1 | tee /tmp/test_process.log

if [ -f "$TEST_PROCESSED" ]; then
    log "数据处理测试成功！"
    echo "  输出文件: $TEST_PROCESSED"
    
    # 显示处理后的数据示例
    echo ""
    echo "处理后的商品示例："
    python3 << EOF
import json
with open('$TEST_PROCESSED', 'r') as f:
    data = json.load(f)
    if data.get('products'):
        p = data['products'][0]
        print(f"  标题: {p.get('title', 'N/A')[:40]}...")
        print(f"  价格: ¥{p.get('price', 0)}")
        print(f"  分类: {p.get('category_douyin', 'N/A')}")
EOF
else
    error "数据处理测试失败"
    exit 1
fi

echo ""
echo "【Step 4】检查上架准备..."

# 检查浏览器
if python3 -c "from playwright.sync_api import sync_playwright" 2>/dev/null; then
    log "Playwright API正常"
else
    warn "Playwright API导入失败"
fi

# 显示配置信息
echo ""
echo "当前配置："
WSY_TOKEN=$(cat "$CONFIG_FILE" | grep '"token"' | head -1 | cut -d'"' -f4)
DY_USERNAME=$(cat "$CONFIG_FILE" | grep '"username"' | head -1 | cut -d'"' -f4)

if [ -n "$WSY_TOKEN" ]; then
    log "WSY Token: 已配置"
else
    warn "WSY Token: 未配置"
fi

if [ -n "$DY_USERNAME" ]; then
    log "抖店账号: $DY_USERNAME"
else
    warn "抖店账号: 未配置"
fi

echo ""
echo "================================"
echo "  测试完成！"
echo "================================"
echo ""
echo "下一步："
echo ""
echo "1. 如果WSY Token未配置："
echo "   编辑: nano $CONFIG_FILE"
echo "   或运行: dyshop-config"
echo ""
echo "2. 如果要实际上架测试："
echo "   bash $SKILL_DIR/scripts/upload.sh --input $TEST_PROCESSED"
echo ""
echo "3. 查看完整文档："
echo "   cat $SKILL_DIR/docs/USAGE.md"
echo ""

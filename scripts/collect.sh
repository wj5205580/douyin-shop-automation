#!/bin/bash
# WSY商品采集脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
LIB_DIR="$SKILL_DIR/lib"
DATA_DIR="$SKILL_DIR/data/raw"
CONFIG_FILE="$SKILL_DIR/config/config.json"

mkdir -p "$DATA_DIR"

# 参数
CATEGORY=""
KEYWORD=""
LIMIT=50
SHOP_ID=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --category)
            CATEGORY="$2"
            shift 2
            ;;
        --keyword)
            KEYWORD="$2"
            shift 2
            ;;
        --limit)
            LIMIT="$2"
            shift 2
            ;;
        --shop)
            SHOP_ID="$2"
            shift 2
            ;;
        *)
            echo "未知参数: $1"
            exit 1
            ;;
    esac
done

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="$DATA_DIR/products_${TIMESTAMP}.json"

echo "开始采集..."
echo "分类: ${CATEGORY:-全部}"
echo "关键词: ${KEYWORD:-无}"
echo "数量: $LIMIT"

# 调用Python采集
python3 "$LIB_DIR/collector.py" \
    --category "$CATEGORY" \
    --keyword "$KEYWORD" \
    --limit "$LIMIT" \
    --shop "$SHOP_ID" \
    --output "$OUTPUT_FILE"

if [ -f "$OUTPUT_FILE" ]; then
    COUNT=$(cat "$OUTPUT_FILE" | grep -c '"id"' || echo "0")
    echo "采集完成: $COUNT 个商品"
    echo "OUTPUT_FILE: $OUTPUT_FILE"
else
    echo "采集失败"
    exit 1
fi

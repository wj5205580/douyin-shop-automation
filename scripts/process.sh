#!/bin/bash
# 商品数据处理脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
LIB_DIR="$SKILL_DIR/lib"
DATA_DIR="$SKILL_DIR/data/processed"
CONFIG_FILE="$SKILL_DIR/config/config.json"

mkdir -p "$DATA_DIR"

# 参数
INPUT_FILE=""
PROFIT=30

case $1 in
    --input)
        INPUT_FILE="$2"
        shift 2
        ;;
esac

while [[ $# -gt 0 ]]; do
    case $1 in
        --profit)
            PROFIT="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

if [ -z "$INPUT_FILE" ] || [ ! -f "$INPUT_FILE" ]; then
    echo "错误: 请指定有效的输入文件 --input"
    exit 1
fi

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="$DATA_DIR/processed_${TIMESTAMP}.json"

echo "开始处理数据..."
echo "输入: $INPUT_FILE"
echo "利润率: $PROFIT%"

python3 "$LIB_DIR/processor.py" \
    --input "$INPUT_FILE" \
    --profit "$PROFIT" \
    --output "$OUTPUT_FILE" \
    --config "$CONFIG_FILE"

if [ -f "$OUTPUT_FILE" ]; then
    COUNT=$(cat "$OUTPUT_FILE" | grep -c '"id"' || echo "0")
    echo "处理完成: $COUNT 个商品"
    echo "OUTPUT_FILE: $OUTPUT_FILE"
else
    echo "处理失败"
    exit 1
fi

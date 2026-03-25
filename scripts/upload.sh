#!/bin/bash
# 抖音小店自动上架脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
LIB_DIR="$SKILL_DIR/lib"
CONFIG_FILE="$SKILL_DIR/config/config.json"
LOG_DIR="$SKILL_DIR/logs"

mkdir -p "$LOG_DIR"

# 参数
INPUT_FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --input)
            INPUT_FILE="$2"
            shift 2
            ;;
        *)
            echo "未知参数: $1"
            exit 1
            ;;
    esac
done

if [ -z "$INPUT_FILE" ] || [ ! -f "$INPUT_FILE" ]; then
    echo "错误: 请指定有效的输入文件 --input"
    exit 1
fi

echo "开始上架..."
echo "输入: $INPUT_FILE"

python3 "$LIB_DIR/uploader.py" \
    --input "$INPUT_FILE" \
    --config "$CONFIG_FILE" \
    --log-dir "$LOG_DIR"

#!/bin/bash
# 一键执行脚本：采集→处理→上架

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$SKILL_DIR/config/config.json"
LOG_DIR="$SKILL_DIR/logs"
DATA_DIR="$SKILL_DIR/data"

# 默认参数
CATEGORY=""
LIMIT=20
PROFIT=30
KEYWORD=""

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --category)
            CATEGORY="$2"
            shift 2
            ;;
        --limit)
            LIMIT="$2"
            shift 2
            ;;
        --profit)
            PROFIT="$2"
            shift 2
            ;;
        --keyword)
            KEYWORD="$2"
            shift 2
            ;;
        *)
            echo "未知参数: $1"
            exit 1
            ;;
    esac
done

if [ -z "$CATEGORY" ] && [ -z "$KEYWORD" ]; then
    error "请指定 --category 或 --keyword"
    exit 1
fi

# 创建日志目录
mkdir -p "$LOG_DIR"
mkdir -p "$DATA_DIR/raw"
mkdir -p "$DATA_DIR/processed"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RUN_LOG="$LOG_DIR/run_$TIMESTAMP.log"

log "========== 抖音小店自动上货开始 ==========" | tee -a "$RUN_LOG"
log "分类: ${CATEGORY:-无} | 关键词: ${KEYWORD:-无} | 数量: $LIMIT | 利润率: $PROFIT%" | tee -a "$RUN_LOG"

# Step 1: 采集商品
log "【Step 1】开始采集商品..." | tee -a "$RUN_LOG"
COLLECT_OUTPUT=$(bash "$SCRIPT_DIR/collect.sh" --category "$CATEGORY" --keyword "$KEYWORD" --limit "$LIMIT" 2>&1)
RAW_FILE=$(echo "$COLLECT_OUTPUT" | grep "OUTPUT_FILE:" | cut -d: -f2 | tr -d ' ')

if [ -z "$RAW_FILE" ] || [ ! -f "$RAW_FILE" ]; then
    error "采集失败，未获取到商品数据" | tee -a "$RUN_LOG"
    exit 1
fi

COLLECT_COUNT=$(echo "$COLLECT_OUTPUT" | grep "采集完成" | grep -oE '[0-9]+' | tail -1)
log "✅ 采集完成: $COLLECT_COUNT 个商品 → $RAW_FILE" | tee -a "$RUN_LOG"

# Step 2: 处理数据
log "【Step 2】开始处理数据..." | tee -a "$RUN_LOG"
PROCESS_OUTPUT=$(bash "$SCRIPT_DIR/process.sh" --input "$RAW_FILE" --profit "$PROFIT" 2>&1)
PROCESSED_FILE=$(echo "$PROCESS_OUTPUT" | grep "OUTPUT_FILE:" | cut -d: -f2 | tr -d ' ')

if [ -z "$PROCESSED_FILE" ] || [ ! -f "$PROCESSED_FILE" ]; then
    error "处理失败" | tee -a "$RUN_LOG"
    exit 1
fi

PROCESS_COUNT=$(echo "$PROCESS_OUTPUT" | grep "处理完成" | grep -oE '[0-9]+' | tail -1)
log "✅ 处理完成: $PROCESS_COUNT 个商品 → $PROCESSED_FILE" | tee -a "$RUN_LOG"

# Step 3: 自动上架
log "【Step 3】开始自动上架..." | tee -a "$RUN_LOG"
UPLOAD_OUTPUT=$(bash "$SCRIPT_DIR/upload.sh" --input "$PROCESSED_FILE" 2>&1)

SUCCESS_COUNT=$(echo "$UPLOAD_OUTPUT" | grep "上架成功" | grep -oE '[0-9]+' | head -1)
FAIL_COUNT=$(echo "$UPLOAD_OUTPUT" | grep "上架失败" | grep -oE '[0-9]+' | head -1)

log "✅ 上架完成: 成功 ${SUCCESS_COUNT:-0} 个, 失败 ${FAIL_COUNT:-0} 个" | tee -a "$RUN_LOG"

# 汇总
log "========== 执行完成 ==========" | tee -a "$RUN_LOG"
log "原始数据: $RAW_FILE" | tee -a "$RUN_LOG"
log "处理后数据: $PROCESSED_FILE" | tee -a "$RUN_LOG"
log "日志文件: $RUN_LOG" | tee -a "$RUN_LOG"

# 发送飞书通知（如果配置了）
if [ -f "$CONFIG_FILE" ]; then
    WEBHOOK=$(cat "$CONFIG_FILE" | grep -o '"feishu_webhook"[^}]*' | cut -d'"' -f4)
    if [ -n "$WEBHOOK" ]; then
        curl -s -X POST "$WEBHOOK" \
            -H "Content-Type: application/json" \
            -d "{\"msg_type\":\"text\",\"content\":{\"text\":\"抖音小店自动上货完成\n分类: ${CATEGORY:-无}\n采集: ${COLLECT_COUNT:-0} 个\n上架成功: ${SUCCESS_COUNT:-0} 个\n上架失败: ${FAIL_COUNT:-0} 个\"}}" > /dev/null
    fi
fi

echo ""
echo "运行日志: $RUN_LOG"

#!/bin/bash
# 抖音小店自动化上货 Skill 安装脚本

set -e

SKILL_NAME="xiaohongshu-qianfan-automation"
SKILL_DIR="$HOME/.agents/skills/$SKILL_NAME"
INSTALL_LOG="/tmp/${SKILL_NAME}_install.log"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')] $1${NC}" | tee -a "$INSTALL_LOG"
}

warn() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')] $1${NC}" | tee -a "$INSTALL_LOG"
}

error() {
    echo -e "${RED}[$(date '+%H:%M:%S')] $1${NC}" | tee -a "$INSTALL_LOG"
}

info() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')] $1${NC}" | tee -a "$INSTALL_LOG"
}

# 检查依赖
check_dependencies() {
    log "检查依赖..."
    
    # Python3
    if ! command -v python3 &> /dev/null; then
        error "未找到 Python3，请先安装"
        exit 1
    fi
    log "✓ Python3: $(python3 --version)"
    
    # pip
    if ! command -v pip3 &> /dev/null; then
        error "未找到 pip3，请先安装"
        exit 1
    fi
    log "✓ pip3: $(pip3 --version)"
    
    # Node.js (用于某些工具)
    if command -v node &> /dev/null; then
        log "✓ Node.js: $(node --version)"
    else
        warn "未找到 Node.js（可选）"
    fi
    
    log "依赖检查完成"
}

# 安装Python包
install_python_packages() {
    log "安装Python依赖..."
    
    pip3 install --user -q playwright requests pillow 2>&1 | tee -a "$INSTALL_LOG"
    
    log "✓ Python包安装完成"
    
    # 安装Playwright浏览器
    log "安装Playwright Chromium浏览器（需要1-2分钟）..."
    python3 -m playwright install chromium 2>&1 | tee -a "$INSTALL_LOG"
    
    log "✓ 浏览器安装完成"
}

# 创建目录结构
create_directories() {
    log "创建目录结构..."
    
    mkdir -p "$SKILL_DIR"/{scripts,lib,config,logs,data/{raw,processed,images},docs,examples}
    
    log "✓ 目录创建完成"
}

# 复制文件
copy_files() {
    log "复制Skill文件..."
    
    # 获取脚本所在目录
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    SOURCE_DIR="$(dirname "$SCRIPT_DIR")"
    
    # 复制核心文件
    cp -r "$SOURCE_DIR"/* "$SKILL_DIR/" 2>/dev/null || true
    
    # 确保脚本可执行
    chmod +x "$SKILL_DIR/scripts/"*.sh
    chmod +x "$SKILL_DIR/lib/"*.py
    
    log "✓ 文件复制完成"
}

# 配置向导
run_config_wizard() {
    info ""
    info "================================"
    info "  抖音小店自动化上货 - 配置向导"
    info "================================"
    info ""
    
    CONFIG_FILE="$SKILL_DIR/config/config.json"
    
    # WSY配置
    info "【Step 1】WSY平台配置"
    read -p "WSY Token (留空稍后配置): " wsy_token
    
    # 抖店配置
    info ""
    info "【Step 2】千帆后台配置"
    read -p "千帆后台登录用户名 (手机号/邮箱): " dy_username
    read -s -p "千帆后台登录密码: " dy_password
    echo ""
    
    # 利润率
    info ""
    info "【Step 3】价格策略"
    read -p "默认利润率 (%，默认30): " profit_rate
    profit_rate=${profit_rate:-30}
    
    # 飞书通知
    info ""
    info "【Step 4】飞书通知（可选）"
    read -p "飞书Webhook URL (留空不启用): " feishu_webhook
    
    # 生成配置文件
    cat > "$CONFIG_FILE" << EOF
{
  "wsy": {
    "base_url": "https://api.wsy.com",
    "token": "${wsy_token}",
    "timeout": 30,
    "retry": 3,
    "delay": 1
  },
  "qianfan": {
    "login_url": "https://ark.xiaohongshu.com/",
    "username": "${dy_username}",
    "password": "${dy_password}",
    "headless": false,
    "slow_mo": 500
  },
  "processing": {
    "profit_rate": ${profit_rate},
    "min_price": 9.9,
    "max_price": 9999,
    "title_max_length": 20,
    "image_quality": 85,
    "image_max_size": 800,
    "forbidden_words": [
      "最强", "第一", "唯一", "国家级", "最高级", "最佳",
      "绝对", "永久", "万能", "特效", "根治"
    ],
    "category_map": {
      "女装": "50000001",
      "男装": "50000002",
      "鞋靴": "50000003",
      "箱包": "50000004",
      "美妆": "50000005",
      "配饰": "50000006",
      "家居": "50000007",
      "数码": "50000008",
      "食品": "50000009",
      "母婴": "50000010"
    },
    "tags_map": {
      "女装": ["OOTD", "穿搭", "显瘦", "氛围感"],
      "美妆": ["种草", "试色", "平价", "学生党"],
      "家居": ["收纳", "改造", "ins风", "好物分享"]
    }
  },
  "upload": {
    "timeout": 30000,
    "retry": 3,
    "delay": 2
  },
  "feishu_webhook": "${feishu_webhook}",
  "notification": {
    "enabled": true,
    "on_success": true,
    "on_failure": true
  }
}
EOF
    
    log "✓ 配置文件生成: $CONFIG_FILE"
}

# 创建快捷命令
create_aliases() {
    log "创建快捷命令..."
    
    SHELL_RC=""
    if [ -f "$HOME/.zshrc" ]; then
        SHELL_RC="$HOME/.zshrc"
    elif [ -f "$HOME/.bashrc" ]; then
        SHELL_RC="$HOME/.bashrc"
    fi
    
    if [ -n "$SHELL_RC" ]; then
        # 检查是否已添加
        if ! grep -q "douyin-shop" "$SHELL_RC" 2>/dev/null; then
            cat >> "$SHELL_RC" << 'EOF'

# 小红书千帆后台自动化上货快捷命令
alias xhsqf='bash ~/.agents/skills/xiaohongshu-qianfan-automation/scripts/run.sh'
alias xhsqf-collect='bash ~/.agents/skills/xiaohongshu-qianfan-automation/scripts/collect.sh'
alias xhsqf-process='bash ~/.agents/skills/xiaohongshu-qianfan-automation/scripts/process.sh'
alias xhsqf-upload='bash ~/.agents/skills/xiaohongshu-qianfan-automation/scripts/upload.sh'
alias xhsqf-config='nano ~/.agents/skills/xiaohongshu-qianfan-automation/config/config.json'
alias xhsqf-logs='tail -f ~/.agents/skills/xiaohongshu-qianfan-automation/logs/*.log'
EOF
            log "✓ 快捷命令已添加到 $SHELL_RC"
            warn "请运行: source $SHELL_RC"
        fi
    fi
}

# 创建定时任务示例
show_cron_example() {
    info ""
    info "【定时任务示例】"
    info "添加到crontab实现自动采集上架："
    info ""
    info "# 每2小时自动采集上架女装"
    info "0 */2 * * * bash $SKILL_DIR/scripts/run.sh --category '女装' --limit 10 >> $SKILL_DIR/logs/cron.log 2>&1"
    info ""
    info "# 每天早上8点采集上架"
    info "0 8 * * * bash $SKILL_DIR/scripts/run.sh --category '家居' --limit 20 >> $SKILL_DIR/logs/cron.log 2>&1"
    info ""
}

# 显示使用说明
show_usage() {
    info ""
    info "================================"
    info "  安装完成！"
    info "================================"
    info ""
    info "📂 安装目录: $SKILL_DIR"
    info "📋 配置文件: $SKILL_DIR/config/config.json"
    info "📝 日志目录: $SKILL_DIR/logs/"
    info ""
    info "🚀 快速开始:"
    info ""
    info "  # 一键执行（采集→处理→上架）"
    info "  dyshop --category '女装' --limit 20 --profit 30"
    info ""
    info "  # 或分步执行"
    info "  dyshop-collect --category '女装' --limit 50"
    info "  dyshop-process --input data/raw/xxx.json --profit 30"
    info "  dyshop-upload --input data/processed/xxx.json"
    info ""
    info "⚙️  常用命令:"
    info "  dyshop-config   # 编辑配置"
    info "  dyshop-logs     # 查看日志"
    info ""
    info "📖 详细文档: $SKILL_DIR/SKILL.md"
    info ""
}

# 主函数
main() {
    log "================================"
    log "  小红书千帆后台自动化上货 Skill 安装"
    log "================================"
    log ""
    
    # 检查是否已安装
    if [ -d "$SKILL_DIR" ] && [ "$1" != "--force" ]; then
        warn "Skill已安装: $SKILL_DIR"
        read -p "是否重新安装? (y/N): " confirm
        if [[ ! $confirm =~ ^[Yy]$ ]]; then
            log "取消安装"
            exit 0
        fi
        rm -rf "$SKILL_DIR"
    fi
    
    # 执行安装步骤
    check_dependencies
    install_python_packages
    create_directories
    copy_files
    run_config_wizard
    create_aliases
    show_cron_example
    show_usage
    
    log "✅ 安装完成！"
    
    # 显示日志位置
    log "安装日志: $INSTALL_LOG"
}

# 运行
main "$@"

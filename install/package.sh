#!/bin/bash
# Skill封装打包脚本

set -e

SKILL_NAME="douyin-shop-automation"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="$SKILL_DIR/dist"
VERSION=$(cat "$SKILL_DIR/_meta.json" | grep '"version"' | cut -d'"' -f4)

mkdir -p "$OUTPUT_DIR"

echo "================================"
echo "  封装 $SKILL_NAME v$VERSION"
echo "================================"
echo ""

# 清理旧的构建
rm -rf "$OUTPUT_DIR"/*

# 创建临时目录
BUILD_DIR=$(mktemp -d)
trap "rm -rf $BUILD_DIR" EXIT

# 复制文件
echo "复制文件..."
rsync -av --exclude='dist' --exclude='.git' --exclude='logs/*' --exclude='data/*' \
    "$SKILL_DIR/" "$BUILD_DIR/$SKILL_NAME/"

# 创建README
cat > "$BUILD_DIR/$SKILL_NAME/README.md" << 'EOF'
# 抖音小店自动化上货系统

从WSY采集商品，自动处理后上架到抖音小店。

## 快速安装

```bash
# 方式1：直接安装
cd douyin-shop-automation
bash install/install.sh

# 方式2：作为OpenClaw Skill安装
# 复制到 ~/.agents/skills/douyin-shop-automation/
```

## 依赖

- Python 3.8+
- pip3
- Playwright

## 安装后使用

```bash
# 一键执行
dyshop --category "女装" --limit 20 --profit 30

# 分步执行
dyshop-collect --category "女装" --limit 50
dyshop-process --input data/raw/xxx.json --profit 30
dyshop-upload --input data/processed/xxx.json
```

详细文档见 SKILL.md
EOF

# 打包
echo "打包..."

# tar.gz
cd "$BUILD_DIR"
tar -czf "$OUTPUT_DIR/${SKILL_NAME}-v${VERSION}.tar.gz" "$SKILL_NAME"
echo "✓ $OUTPUT_DIR/${SKILL_NAME}-v${VERSION}.tar.gz"

# zip
zip -rq "$OUTPUT_DIR/${SKILL_NAME}-v${VERSION}.zip" "$SKILL_NAME"
echo "✓ $OUTPUT_DIR/${SKILL_NAME}-v${VERSION}.zip"

# 创建安装包（包含自动安装脚本）
cat > "$BUILD_DIR/install-${SKILL_NAME}.sh" << 'EOFSCRIPT'
#!/bin/bash
# 抖音小店自动化上货 - 自动安装包

set -e

echo "正在解压安装包..."

# 提取嵌入的数据
ARCHIVE=$(awk '/^__ARCHIVE_BELOW__/ {print NR + 1; exit 0; }' "$0")
tail -n+$ARCHIVE "$0" | tar -xz

# 运行安装
cd douyin-shop-automation
bash install/install.sh

exit 0

__ARCHIVE_BELOW__
EOFSCRIPT

# 追加tar数据
cat "$OUTPUT_DIR/${SKILL_NAME}-v${VERSION}.tar.gz" >> "$BUILD_DIR/install-${SKILL_NAME}.sh"
chmod +x "$BUILD_DIR/install-${SKILL_NAME}.sh"
cp "$BUILD_DIR/install-${SKILL_NAME}.sh" "$OUTPUT_DIR/"
echo "✓ $OUTPUT_DIR/install-${SKILL_NAME}.sh"

echo ""
echo "================================"
echo "  封装完成！"
echo "================================"
echo ""
echo "输出文件:"
ls -lh "$OUTPUT_DIR/"
echo ""
echo "分发方式:"
echo ""
echo "1. 完整安装包（推荐）:"
echo "   $OUTPUT_DIR/install-${SKILL_NAME}.sh"
echo "   使用: bash install-${SKILL_NAME}.sh"
echo ""
echo "2. 压缩包:"
echo "   $OUTPUT_DIR/${SKILL_NAME}-v${VERSION}.tar.gz"
echo "   $OUTPUT_DIR/${SKILL_NAME}-v${VERSION}.zip"
echo "   解压后运行: bash install/install.sh"
echo ""
echo "3. 作为OpenClaw Skill:"
echo "   复制到: ~/.agents/skills/"
echo ""

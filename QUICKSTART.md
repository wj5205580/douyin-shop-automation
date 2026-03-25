# 抖音小店自动化上货 - 快速开始

## 🎯 5分钟快速上手

### 1️⃣ 安装（1分钟）
```bash
# 下载安装包后运行
bash install-douyin-shop-automation.sh
```

### 2️⃣ 配置（2分钟）
```bash
# 编辑配置
dyshop-config

# 填写：
# - WSY Token（从WSY平台获取）
# - 抖店登录账号密码
```

### 3️⃣ 测试（1分钟）
```bash
# 运行测试
bash ~/.agents/skills/douyin-shop-automation/install/test.sh
```

### 4️⃣ 运行（1分钟）
```bash
# 一键执行
dyshop --category "女装" --limit 10
```

---

## 📋 常用命令速查

| 命令 | 功能 |
|------|------|
| `dyshop` | 一键执行完整流程 |
| `dyshop-collect` | 仅采集商品 |
| `dyshop-process` | 仅处理数据 |
| `dyshop-upload` | 仅上架商品 |
| `dyshop-config` | 编辑配置 |
| `dyshop-logs` | 查看日志 |

---

## 💡 使用示例

### 示例1：采集女装类目
```bash
dyshop --category "女装" --limit 50 --profit 40
```

### 示例2：搜索关键词
```bash
dyshop --keyword "连衣裙" --limit 20
```

### 示例3：分步操作
```bash
# 采集
dyshop-collect --category "家居" --limit 100

# 处理（50%利润）
dyshop-process --input data/raw/xxx.json --profit 50

# 上架
dyshop-upload --input data/processed/xxx.json
```

---

## ⚠️ 重要提示

1. **首次上架前请先测试**
   ```bash
   bash ~/.agents/skills/douyin-shop-automation/install/test.sh
   ```

2. **控制上架频率**
   - 建议每小时不超过20个商品
   - 避免被抖店风控

3. **保存Cookie**
   - 首次登录抖店后保存cookie
   - 后续自动登录

4. **检查日志**
   ```bash
   # 实时查看日志
   tail -f ~/.agents/skills/douyin-shop-automation/logs/*.log
   ```

---

## 📚 更多文档

- 完整手册：`docs/USAGE.md`
- Skill说明：`SKILL.md`
- 配置参考：`config/config.json`

---

## 🆘 遇到问题？

1. 查看日志：`dyshop-logs`
2. 检查配置：`dyshop-config`
3. 重新测试：`bash install/test.sh`

**祝你上架顺利，生意兴隆！** 🎉

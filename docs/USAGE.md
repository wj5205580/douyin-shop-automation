# 抖音小店自动化上货 - 完整使用手册

## 📦 安装

### 方式1：一键安装（推荐）
```bash
bash install-douyin-shop-automation.sh
```

### 方式2：手动安装
```bash
tar -xzf douyin-shop-automation-v1.0.0.tar.gz
cd douyin-shop-automation
bash install/install.sh
```

### 方式3：OpenClaw Skill
```bash
# 复制到skills目录
cp -r douyin-shop-automation ~/.agents/skills/
```

---

## ⚙️ 配置

安装后会自动引导配置，或手动编辑：

```bash
nano ~/.agents/skills/douyin-shop-automation/config/config.json
```

### 必填配置

| 配置项 | 说明 | 获取方式 |
|--------|------|----------|
| `wsy.token` | WSY平台Token | WSY官网个人中心获取 |
| `douyin.username` | 抖店登录账号 | 手机号/邮箱 |
| `douyin.password` | 抖店登录密码 | - |

### 选填配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `processing.profit_rate` | 利润率(%) | 30 |
| `processing.min_price` | 最低售价 | 9.9 |
| `processing.max_price` | 最高售价 | 9999 |
| `feishu_webhook` | 飞书通知 | 空 |

---

## 🚀 使用

### 一键执行（推荐）
```bash
dyshop --category "女装" --limit 20 --profit 30
```

### 分步执行
```bash
# 1. 采集商品
dyshop-collect --category "女装" --limit 50

# 2. 处理数据
dyshop-process --input data/raw/products_xxx.json --profit 30

# 3. 上架商品
dyshop-upload --input data/processed/processed_xxx.json
```

### 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `--category` | 商品分类 | "女装", "家居", "数码" |
| `--keyword` | 搜索关键词 | "连衣裙", "收纳盒" |
| `--limit` | 采集数量 | 20, 50, 100 |
| `--profit` | 利润率(%) | 30, 50, 100 |
| `--shop` | 店铺ID | 用于采集指定店铺 |

---

## 📊 工作流程

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   WSY采集   │ -> │  数据处理   │ -> │  图片处理   │ -> │  抖店上架   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
      │                   │                   │                   │
   商品列表           标题优化            压缩去水印          自动填表
   价格库存           价格计算            格式转换            图片上传
   主图详情           分类映射            临时保存            提交审核
```

---

## ⏰ 定时任务

### 编辑crontab
```bash
crontab -e
```

### 添加任务
```bash
# 每2小时自动采集上架
0 */2 * * * bash ~/.agents/skills/douyin-shop-automation/scripts/run.sh --category "女装" --limit 10 >> ~/.agents/skills/douyin-shop-automation/logs/cron.log 2>&1

# 每天早上8点执行
0 8 * * * bash ~/.agents/skills/douyin-shop-automation/scripts/run.sh --category "家居" --limit 20 >> ~/.agents/skills/douyin-shop-automation/logs/cron.log 2>&1

# 每晚10点采集爆款
0 22 * * * bash ~/.agents/skills/douyin-shop-automation/scripts/run.sh --keyword "爆款" --limit 30 >> ~/.agents/skills/douyin-shop-automation/logs/cron.log 2>&1
```

---

## 📁 目录结构

```
~/.agents/skills/douyin-shop-automation/
├── config/
│   └── config.json          # 配置文件
├── scripts/
│   ├── run.sh               # 一键执行
│   ├── collect.sh           # 采集脚本
│   ├── process.sh           # 处理脚本
│   └── upload.sh            # 上架脚本
├── lib/
│   ├── collector.py         # WSY采集器
│   ├── processor.py         # 数据处理器
│   └── uploader.py          # 抖店上传器
├── data/
│   ├── raw/                 # 原始数据
│   ├── processed/           # 处理后数据
│   └── images/              # 图片缓存
├── logs/                    # 日志文件
└── docs/                    # 文档
```

---

## 🔧 故障排查

### 采集失败
```bash
# 检查WSY Token是否有效
curl -H "Authorization: Bearer YOUR_TOKEN" https://api.wsy.com/api/test

# 查看采集日志
tail -f ~/.agents/skills/douyin-shop-automation/logs/collect_*.log
```

### 上架失败
```bash
# 检查浏览器安装
python3 -m playwright install chromium

# 手动运行上架查看错误
python3 ~/.agents/skills/douyin-shop-automation/lib/uploader.py --input data/processed/xxx.json
```

### 常见问题

**Q: WSY是什么？**
A: WSY是货源平台，类似1688、拼多多批发。需要自行注册获取Token。

**Q: 抖店需要手动登录吗？**
A: 首次需要手动登录，保存cookie后后续自动登录。

**Q: 支持多店铺吗？**
A: 支持，在config.json中配置多个店铺，上架时指定。

**Q: 会封号吗？**
A: 控制上架频率（建议每小时不超过20个），模拟人工操作，降低风险。

---

## 📝 更新日志

### v1.0.0 (2026-03-25)
- 初始版本
- 支持WSY采集
- 支持数据处理（标题优化、价格计算）
- 支持抖店自动上架
- 支持定时任务
- 支持飞书通知

---

## 📞 支持

遇到问题？
1. 查看日志：`dyshop-logs`
2. 检查配置：`dyshop-config`
3. 查看文档：`cat ~/.agents/skills/douyin-shop-automation/SKILL.md`

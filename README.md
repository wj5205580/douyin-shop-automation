# 小红书千帆后台自动化上货系统

[![Release](https://img.shields.io/github/v/release/wj5205580/xiaohongshu-qianfan-automation)](https://github.com/wj5205580/xiaohongshu-qianfan-automation/releases)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)

> 从WSY采集商品，自动处理后上架到小红书千帆后台的完整自动化解决方案

---

## ✨ 功能特性

- 🚀 **一键上货** - 采集→处理→上架全自动
- 🔍 **智能采集** - 支持WSY分类/关键词/店铺采集
- 🎨 **数据处理** - 标题优化（小红书风格）、价格计算、图片压缩
- 🏷️ **自动标签** - 自动生成小红书话题标签（OOTD、种草等）
- 🤖 **自动上架** - Playwright模拟人工操作千帆后台
- ⏰ **定时任务** - 支持crontab定时执行
- 📱 **飞书通知** - 执行结果实时推送

---

## 📦 安装

### 方式一：一键安装（推荐）

```bash
curl -fsSL https://github.com/wj5205580/xiaohongshu-qianfan-automation/releases/download/v1.0.0/install-xiaohongshu-qianfan-automation.sh | bash
```

### 方式二：手动安装

```bash
# 下载压缩包
wget https://github.com/wj5205580/xiaohongshu-qianfan-automation/releases/download/v1.0.0/xiaohongshu-qianfan-automation-v1.0.0.tar.gz

# 解压安装
tar -xzf xiaohongshu-qianfan-automation-v1.0.0.tar.gz
cd xiaohongshu-qianfan-automation
bash install/install.sh
```

### 方式三：OpenClaw Skill

```bash
# 复制到OpenClaw技能目录
cp -r xiaohongshu-qianfan-automation ~/.agents/skills/
```

---

## ⚡ 快速开始

### 1. 配置

```bash
# 编辑配置
xhsqf-config

# 填写：
# - WSY Token（从WSY平台获取）
# - 千帆后台登录账号密码
# - 飞书Webhook（可选）
```

### 2. 测试

```bash
bash ~/.agents/skills/xiaohongshu-qianfan-automation/install/test.sh
```

### 3. 运行

```bash
# 一键执行
xhsqf --category "女装" --limit 20 --profit 30
```

---

## 📖 使用说明

### 常用命令

| 命令 | 功能 |
|------|------|
| `xhsqf` | 一键执行完整流程 |
| `xhsqf-collect` | 仅采集商品 |
| `xhsqf-process` | 仅处理数据 |
| `xhsqf-upload` | 仅上架商品 |
| `xhsqf-config` | 编辑配置 |
| `xhsqf-logs` | 查看日志 |

### 参数说明

```bash
xhsqf --category "女装" --limit 50 --profit 30
```

| 参数 | 说明 | 示例 |
|------|------|------|
| `--category` | 商品分类 | "女装", "家居", "数码" |
| `--keyword` | 搜索关键词 | "连衣裙", "收纳盒" |
| `--limit` | 采集数量 | 20, 50, 100 |
| `--profit` | 利润率(%) | 30, 50, 100 |
| `--shop` | 店铺ID | 采集指定店铺 |

---

## 🔄 工作流程

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   WSY采集   │ -> │  数据处理   │ -> │  图片处理   │ -> │ 千帆上架   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
      │                   │                   │                   │
   商品列表           标题优化            压缩去水印          自动填表
   价格库存           价格计算            格式转换            图片上传
   主图详情           分类映射            临时保存            添加标签
                                          话题生成            提交审核
```

---

## ⏰ 定时任务

```bash
# 编辑crontab
crontab -e

# 每2小时自动采集上架
0 */2 * * * bash ~/.agents/skills/xiaohongshu-qianfan-automation/scripts/run.sh --category "女装" --limit 10 >> ~/.agents/skills/xiaohongshu-qianfan-automation/logs/cron.log 2>&1

# 每天早上8点执行
0 8 * * * bash ~/.agents/skills/xiaohongshu-qianfan-automation/scripts/run.sh --category "家居" --limit 20 >> ~/.agents/skills/xiaohongshu-qianfan-automation/logs/cron.log 2>&1
```

---

## 📁 目录结构

```
~/.agents/skills/xiaohongshu-qianfan-automation/
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
│   └── uploader.py          # 千帆后台上传器
├── data/
│   ├── raw/                 # 原始数据
│   └── processed/           # 处理后数据
├── logs/                    # 日志文件
├── docs/
│   └── USAGE.md            # 详细文档
└── install/
    ├── install.sh          # 安装脚本
    └── test.sh             # 测试脚本
```

---

## 🔧 配置说明

编辑 `config/config.json`：

```json
{
  "wsy": {
    "token": "YOUR_WSY_TOKEN",
    "timeout": 30
  },
  "qianfan": {
    "username": "YOUR_PHONE",
    "password": "YOUR_PASSWORD"
  },
  "processing": {
    "profit_rate": 30,
    "min_price": 9.9,
    "max_price": 9999,
    "category_map": {
      "女装": "50000001",
      "男装": "50000002",
      "美妆": "50000005"
    },
    "tags_map": {
      "女装": ["OOTD", "穿搭", "显瘦", "氛围感"],
      "美妆": ["种草", "试色", "平价", "学生党"]
    }
  },
  "feishu_webhook": "YOUR_FEISHU_WEBHOOK"
}
```

---

## ⚠️ 注意事项

1. **控制上架频率** - 建议每小时不超过20个商品
2. **首次需登录** - 首次上架需手动登录千帆后台保存cookie
3. **标题长度** - 小红书标题限制20字以内，要有关键词
4. **话题标签** - 自动添加OOTD、种草等小红书热门标签
5. **检查日志** - 遇到问题查看 `xhsqf-logs`

---

## 📝 更新日志

### v1.0.0 (2026-03-25)
- 🎉 初始版本发布
- ✅ WSY平台商品采集
- ✅ 小红书风格数据处理（标题、标签）
- ✅ 千帆后台自动上架
- ✅ 自动添加话题标签
- ✅ 定时任务支持
- ✅ 飞书通知集成

---

## 🤝 贡献

欢迎提交Issue和PR！

---

## 📄 许可

MIT License

---

## 💬 支持

- 文档：[docs/USAGE.md](docs/USAGE.md)
- 快速开始：[QUICKSTART.md](QUICKSTART.md)
- 问题反馈：[GitHub Issues](https://github.com/wj5205580/xiaohongshu-qianfan-automation/issues)

**祝您小红书爆单！** 🎉

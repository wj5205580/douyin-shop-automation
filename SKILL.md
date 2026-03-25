---
name: douyin-shop-automation
description: 抖音小店自动化上货系统 - 从WSY采集到抖音小店上架的完整链路。支持商品采集、数据清洗、自动上架、库存监控。
---

# 抖音小店自动化上货系统

从WSY采集商品数据，自动处理（去水印、改价、优化标题），然后通过Playwright自动上传到抖音小店。

## 核心功能

### 1. 商品采集
- WSY平台商品抓取
- 支持分类/关键词/店铺采集
- 自动获取商品图片、标题、价格、详情

### 2. 数据处理
- 图片去水印
- 标题优化（加热搜词，小红书风格）
- 价格调整（利润率设置）
- 分类映射（WSY分类→千帆后台分类）
- 标签生成（小红书话题标签）

### 3. 自动上架
- Playwright模拟人工操作
- 自动填充商品信息
- 批量上传图片
- 自动添加话题标签
- 自动提交审核

### 4. 库存监控
- 实时监控在售商品
- 库存预警
- 自动补货提醒

## 快速开始

### 采集商品
```bash
bash ~/.agents/skills/douyin-shop-automation/scripts/collect.sh --category "女装" --limit 50
```

### 处理数据
```bash
bash ~/.agents/skills/douyin-shop-automation/scripts/process.sh --input data/raw/xxx.json --profit 30
```

### 自动上架
```bash
bash ~/.agents/skills/douyin-shop-automation/scripts/upload.sh --input data/processed/xxx.json
```

### 一键执行（采集→处理→上架）
```bash
bash ~/.agents/skills/douyin-shop-automation/scripts/run.sh --category "女装" --limit 20 --profit 30
```

## 配置文件

编辑 `config/config.json` 设置：
- WSY账号
- 千帆后台登录信息
- 价格策略
- 分类映射
- 小红书话题标签

## 定时任务

每2小时自动采集上架：
```bash
# 添加到crontab
0 */2 * * * bash ~/.agents/skills/douyin-shop-automation/scripts/run.sh --category "女装" --limit 10
```

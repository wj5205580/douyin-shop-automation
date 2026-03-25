#!/usr/bin/env python3
"""
商品数据处理器
功能：图片处理、标题优化、价格调整、分类映射
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from PIL import Image
import requests
from io import BytesIO

class ProductProcessor:
    def __init__(self, config_file=None):
        self.config = self._load_config(config_file)
        self.hot_words = self._load_hot_words()
        
    def _load_config(self, config_file):
        """加载配置"""
        default_config = {
            'profit_rate': 30,  # 默认利润率
            'min_price': 9.9,   # 最低价格
            'max_price': 9999,  # 最高价格
            'title_max_length': 30,  # 标题最大长度
            'category_map': {},  # 分类映射
            'forbidden_words': [],  # 违禁词
            'image_quality': 85,  # 图片压缩质量
            'image_max_size': 800,  # 图片最大边长
        }
        
        if config_file and os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                default_config.update(config.get('processing', {}))
        
        return default_config
    
    def _load_hot_words(self):
        """加载热搜词库"""
        # 可以对接外部API或本地文件
        return {
            '女装': ['新款', '爆款', '显瘦', '韩版', 'ins风'],
            '男装': ['潮牌', '宽松', '工装', '休闲'],
            '家居': ['北欧', '简约', '网红', '收纳'],
            '数码': ['智能', '便携', '高颜值', '黑科技'],
        }
    
    def process_products(self, products, profit_rate=None):
        """批量处理商品"""
        if profit_rate is None:
            profit_rate = self.config['profit_rate']
        
        processed = []
        for i, product in enumerate(products):
            try:
                print(f"处理商品 {i+1}/{len(products)}: {product.get('title', '未知')[:30]}...")
                
                # 处理标题
                product['title'] = self._optimize_title(product['title'], product.get('category', ''))
                
                # 处理价格
                product['price'] = self._calculate_price(product['price'], profit_rate)
                
                # 处理分类
                product['category_douyin'] = self._map_category(product.get('category', ''))
                
                # 处理图片
                product['images_processed'] = self._process_images(product.get('images', []))
                
                # 处理详情
                product['description'] = self._clean_description(product.get('description', ''))
                
                # 移除违禁词
                product = self._remove_forbidden_words(product)
                
                processed.append(product)
                
            except Exception as e:
                print(f"  处理失败: {e}")
                continue
        
        return processed
    
    def _optimize_title(self, title, category):
        """优化标题"""
        if not title:
            return "优质商品"
        
        # 清理原标题
        title = re.sub(r'[【\[\(].*?[\)\]】]', '', title)  # 移除括号内容
        title = re.sub(r'\s+', ' ', title).strip()
        
        # 添加热搜词
        hot_words = self.hot_words.get(category, [])
        if hot_words and len(title) < self.config['title_max_length'] - 4:
            hot_word = hot_words[0] if hot_words else ''
            if hot_word and hot_word not in title:
                title = f"{hot_word}{title}"
        
        # 截断
        if len(title) > self.config['title_max_length']:
            title = title[:self.config['title_max_length']-3] + '...'
        
        return title
    
    def _calculate_price(self, original_price, profit_rate):
        """计算售价"""
        if original_price <= 0:
            original_price = 29.9
        
        # 成本价（假设WSY价格是批发价的70%）
        cost_price = original_price * 0.7
        
        # 计算售价
        price = cost_price * (1 + profit_rate / 100)
        
        # 心理定价
        price = round(price * 0.99, 2)  # 9.9, 19.9 等
        
        # 限制范围
        price = max(self.config['min_price'], min(price, self.config['max_price']))
        
        return price
    
    def _map_category(self, wsy_category):
        """分类映射"""
        category_map = self.config.get('category_map', {})
        
        # 直接映射
        if wsy_category in category_map:
            return category_map[wsy_category]
        
        # 关键词匹配
        for key, value in category_map.items():
            if key in wsy_category:
                return value
        
        # 默认分类
        return '20000'  # 抖店默认分类ID
    
    def _process_images(self, images):
        """处理图片"""
        processed = []
        for img_url in images[:5]:  # 最多5张
            try:
                # 下载图片
                response = requests.get(img_url, timeout=10)
                img = Image.open(BytesIO(response.content))
                
                # 转换为RGB
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 压缩尺寸
                max_size = self.config['image_max_size']
                if max(img.size) > max_size:
                    ratio = max_size / max(img.size)
                    new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # 保存
                buffer = BytesIO()
                img.save(buffer, format='JPEG', quality=self.config['image_quality'])
                
                processed.append({
                    'url': img_url,
                    'size': img.size,
                    'data': buffer.getvalue(),
                })
                
            except Exception as e:
                print(f"  图片处理失败: {e}")
                continue
        
        return processed
    
    def _clean_description(self, description):
        """清理详情描述"""
        if not description:
            return ""
        
        # 移除链接
        description = re.sub(r'https?://\S+', '', description)
        
        # 移除联系方式
        description = re.sub(r'\d{11}', '', description)  # 手机号
        description = re.sub(r'[\w.-]+@[\w.-]+', '', description)  # 邮箱
        
        # 清理HTML
        description = re.sub(r'<[^>]+>', '', description)
        
        return description.strip()
    
    def _remove_forbidden_words(self, product):
        """移除违禁词"""
        forbidden = self.config.get('forbidden_words', [])
        
        for word in forbidden:
            product['title'] = product['title'].replace(word, '')
            product['description'] = product['description'].replace(word, '')
        
        return product
    
    def save_products(self, products, output_file):
        """保存处理后的商品"""
        data = {
            'metadata': {
                'count': len(products),
                'processed_at': datetime.now().isoformat(),
                'profit_rate': self.config['profit_rate'],
            },
            'products': products,
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"已保存 {len(products)} 个商品到: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='商品数据处理器')
    parser.add_argument('--input', required=True, help='输入文件')
    parser.add_argument('--output', required=True, help='输出文件')
    parser.add_argument('--profit', type=int, default=30, help='利润率(%)')
    parser.add_argument('--config', help='配置文件')
    
    args = parser.parse_args()
    
    # 加载商品
    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    products = data.get('products', [])
    print(f"加载 {len(products)} 个商品")
    
    # 处理
    processor = ProductProcessor(args.config)
    processed = processor.process_products(products, args.profit)
    
    # 保存
    processor.save_products(processed, args.output)
    print(f"处理完成: {len(processed)} 个商品")


if __name__ == '__main__':
    main()

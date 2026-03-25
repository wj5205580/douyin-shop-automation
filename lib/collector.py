#!/usr/bin/env python3
"""
WSY商品采集器
支持：分类采集、关键词搜索、店铺采集
"""

import argparse
import json
import os
import sys
import time
import requests
from urllib.parse import quote, urlencode
from datetime import datetime

class WSYCollector:
    def __init__(self, config_file=None):
        self.config = self._load_config(config_file)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Origin': 'https://www.wsy.com',
            'Referer': 'https://www.wsy.com/',
        })
        
    def _load_config(self, config_file):
        """加载配置文件"""
        default_config = {
            'wsy_base_url': 'https://api.wsy.com',
            'wsy_token': '',
            'timeout': 30,
            'retry': 3,
            'delay': 1,
        }
        
        if config_file and os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                default_config.update(config)
        
        return default_config
    
    def search_by_keyword(self, keyword, limit=50):
        """关键词搜索"""
        products = []
        page = 1
        
        print(f"搜索关键词: {keyword}")
        
        while len(products) < limit:
            try:
                url = f"{self.config['wsy_base_url']}/api/search"
                params = {
                    'keyword': keyword,
                    'page': page,
                    'pageSize': min(50, limit - len(products)),
                    'sort': 'sales_desc',  # 按销量排序
                }
                
                response = self.session.get(url, params=params, timeout=self.config['timeout'])
                data = response.json()
                
                if data.get('code') != 200:
                    print(f"API错误: {data.get('message')}")
                    break
                
                items = data.get('data', {}).get('list', [])
                if not items:
                    break
                
                for item in items:
                    product = self._parse_product(item)
                    if product:
                        products.append(product)
                
                print(f"  第{page}页: 获取 {len(items)} 个商品，总计 {len(products)}")
                
                if len(items) < 50:
                    break
                
                page += 1
                time.sleep(self.config['delay'])
                
            except Exception as e:
                print(f"请求失败: {e}")
                time.sleep(2)
                continue
        
        return products[:limit]
    
    def search_by_category(self, category, limit=50):
        """分类采集"""
        products = []
        page = 1
        
        print(f"采集分类: {category}")
        
        # 分类映射（需要根据实际情况配置）
        category_map = self.config.get('category_map', {})
        cat_id = category_map.get(category, '')
        
        while len(products) < limit:
            try:
                url = f"{self.config['wsy_base_url']}/api/category/products"
                params = {
                    'categoryId': cat_id,
                    'categoryName': category,
                    'page': page,
                    'pageSize': min(50, limit - len(products)),
                    'sort': 'sales_desc',
                }
                
                response = self.session.get(url, params=params, timeout=self.config['timeout'])
                data = response.json()
                
                if data.get('code') != 200:
                    print(f"API错误: {data.get('message')}")
                    break
                
                items = data.get('data', {}).get('list', [])
                if not items:
                    break
                
                for item in items:
                    product = self._parse_product(item)
                    if product:
                        products.append(product)
                
                print(f"  第{page}页: 获取 {len(items)} 个商品，总计 {len(products)}")
                
                if len(items) < 50:
                    break
                
                page += 1
                time.sleep(self.config['delay'])
                
            except Exception as e:
                print(f"请求失败: {e}")
                time.sleep(2)
                continue
        
        return products[:limit]
    
    def search_by_shop(self, shop_id, limit=50):
        """店铺采集"""
        products = []
        page = 1
        
        print(f"采集店铺: {shop_id}")
        
        while len(products) < limit:
            try:
                url = f"{self.config['wsy_base_url']}/api/shop/products"
                params = {
                    'shopId': shop_id,
                    'page': page,
                    'pageSize': min(50, limit - len(products)),
                }
                
                response = self.session.get(url, params=params, timeout=self.config['timeout'])
                data = response.json()
                
                items = data.get('data', {}).get('list', [])
                if not items:
                    break
                
                for item in items:
                    product = self._parse_product(item)
                    if product:
                        products.append(product)
                
                print(f"  第{page}页: 获取 {len(items)} 个商品，总计 {len(products)}")
                
                if len(items) < 50:
                    break
                
                page += 1
                time.sleep(self.config['delay'])
                
            except Exception as e:
                print(f"请求失败: {e}")
                time.sleep(2)
                continue
        
        return products[:limit]
    
    def _parse_product(self, item):
        """解析商品数据"""
        try:
            product = {
                'id': str(item.get('id', '')),
                'title': item.get('title', ''),
                'price': float(item.get('price', 0)),
                'original_price': float(item.get('originalPrice', 0)),
                'sales': int(item.get('sales', 0)),
                'shop_name': item.get('shopName', ''),
                'shop_id': str(item.get('shopId', '')),
                'category': item.get('category', ''),
                'main_image': item.get('mainImage', ''),
                'images': item.get('images', []),
                'detail_images': item.get('detailImages', []),
                'description': item.get('description', ''),
                'sku_list': item.get('skuList', []),
                'source_url': item.get('url', ''),
                'collected_at': datetime.now().isoformat(),
            }
            return product
        except Exception as e:
            print(f"解析商品失败: {e}")
            return None
    
    def save_products(self, products, output_file):
        """保存商品数据"""
        data = {
            'metadata': {
                'count': len(products),
                'collected_at': datetime.now().isoformat(),
                'source': 'wsy',
            },
            'products': products,
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"已保存 {len(products)} 个商品到: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='WSY商品采集器')
    parser.add_argument('--category', help='分类名称')
    parser.add_argument('--keyword', help='搜索关键词')
    parser.add_argument('--shop', help='店铺ID')
    parser.add_argument('--limit', type=int, default=50, help='采集数量')
    parser.add_argument('--output', required=True, help='输出文件路径')
    parser.add_argument('--config', help='配置文件路径')
    
    args = parser.parse_args()
    
    collector = WSYCollector(args.config)
    
    # 根据参数选择采集方式
    if args.keyword:
        products = collector.search_by_keyword(args.keyword, args.limit)
    elif args.category:
        products = collector.search_by_category(args.category, args.limit)
    elif args.shop:
        products = collector.search_by_shop(args.shop, args.limit)
    else:
        print("请指定 --keyword, --category 或 --shop")
        sys.exit(1)
    
    # 保存结果
    collector.save_products(products, args.output)
    print(f"采集完成: {len(products)} 个商品")


if __name__ == '__main__':
    main()

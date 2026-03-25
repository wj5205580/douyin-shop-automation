#!/usr/bin/env python3
"""
抖音小店自动上架机器人
使用Playwright模拟人工操作
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from typing import List, Dict

try:
    from playwright.sync_api import sync_playwright, Page, Browser
except ImportError:
    print("请先安装Playwright: pip install playwright")
    print("然后安装浏览器: playwright install chromium")
    sys.exit(1)


class DouyinUploader:
    def __init__(self, config_file=None, log_dir=None):
        self.config = self._load_config(config_file)
        self.log_dir = log_dir or './logs'
        self.browser = None
        self.page = None
        self.results = {
            'success': 0,
            'failed': 0,
            'details': [],
        }
        
    def _load_config(self, config_file):
        """加载配置"""
        default_config = {
            'douyin': {
                'login_url': 'https://fxg.jinritemai.com/',
                'username': '',
                'password': '',
                'headless': False,
                'slow_mo': 500,
            },
            'upload': {
                'timeout': 30000,
                'retry': 3,
                'delay': 2,
            }
        }
        
        if config_file and os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                default_config.update(config)
        
        return default_config
    
    def _log(self, message, level='INFO'):
        """记录日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] [{level}] {message}"
        print(log_message)
        
        # 写入日志文件
        log_file = os.path.join(self.log_dir, f'upload_{datetime.now().strftime("%Y%m%d")}.log')
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
    
    def start_browser(self):
        """启动浏览器"""
        self._log("启动浏览器...")
        
        playwright = sync_playwright().start()
        
        browser_config = self.config.get('douyin', {})
        
        self.browser = playwright.chromium.launch(
            headless=browser_config.get('headless', False),
            slow_mo=browser_config.get('slow_mo', 500),
        )
        
        context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        )
        
        self.page = context.new_page()
        self._log("浏览器启动完成")
        
    def login(self):
        """登录抖音小店"""
        self._log("开始登录...")
        
        config = self.config.get('douyin', {})
        self.page.goto(config.get('login_url', 'https://fxg.jinritemai.com/'))
        
        # 等待登录页面加载
        self.page.wait_for_load_state('networkidle')
        
        # 这里需要手动登录或使用cookie
        # 建议先手动登录一次，保存cookie后后续使用
        
        self._log("请手动完成登录，登录完成后按回车继续...")
        input()
        
        # 保存cookie
        self._save_cookies()
        
        self._log("登录完成")
    
    def _save_cookies(self):
        """保存cookie"""
        cookies = self.page.context.cookies()
        cookie_file = os.path.join(self.log_dir, 'cookies.json')
        with open(cookie_file, 'w', encoding='utf-8') as f:
            json.dump(cookies, f)
        self._log(f"Cookie已保存: {cookie_file}")
    
    def _load_cookies(self):
        """加载cookie"""
        cookie_file = os.path.join(self.log_dir, 'cookies.json')
        if os.path.exists(cookie_file):
            with open(cookie_file, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            self.page.context.add_cookies(cookies)
            self._log("Cookie已加载")
            return True
        return False
    
    def upload_product(self, product: Dict) -> bool:
        """上传单个商品"""
        try:
            self._log(f"开始上架: {product.get('title', '未知')[:30]}...")
            
            # 进入商品发布页面
            self.page.goto('https://fxg.jinritemai.com/product/create')
            self.page.wait_for_load_state('networkidle')
            
            # 等待页面加载
            time.sleep(2)
            
            # 1. 选择类目
            self._select_category(product.get('category_douyin', ''))
            
            # 2. 填写标题
            self._fill_title(product.get('title', ''))
            
            # 3. 上传主图
            self._upload_images(product.get('images_processed', []))
            
            # 4. 填写价格
            self._fill_price(product.get('price', 0))
            
            # 5. 填写库存
            self._fill_stock(999)  # 默认库存
            
            # 6. 填写详情
            self._fill_description(product.get('description', ''))
            
            # 7. 提交审核
            self._submit_product()
            
            self._log(f"上架成功: {product.get('title', '未知')[:30]}...")
            return True
            
        except Exception as e:
            self._log(f"上架失败: {e}", 'ERROR')
            return False
    
    def _select_category(self, category_id: str):
        """选择商品类目"""
        try:
            # 点击类目选择框
            self.page.click('.category-selector')
            time.sleep(1)
            
            # 根据category_id选择类目（这里需要根据实际情况调整）
            # 简化版：直接搜索类目
            if category_id:
                search_box = self.page.locator('.category-search input')
                search_box.fill(category_id)
                time.sleep(1)
                
                # 选择第一个结果
                self.page.click('.category-result-item:first-child')
                time.sleep(1)
            
            # 确认选择
            self.page.click('.category-confirm-btn')
            time.sleep(1)
            
        except Exception as e:
            self._log(f"类目选择失败: {e}", 'WARNING')
    
    def _fill_title(self, title: str):
        """填写商品标题"""
        try:
            title_input = self.page.locator('input[placeholder*="标题"], .product-title input')
            title_input.fill(title)
            time.sleep(0.5)
        except Exception as e:
            self._log(f"标题填写失败: {e}", 'WARNING')
    
    def _upload_images(self, images: List):
        """上传商品图片"""
        try:
            if not images:
                self._log("没有图片需要上传", 'WARNING')
                return
            
            # 找到文件上传input
            file_input = self.page.locator('input[type="file"]').first
            
            # 准备图片文件路径
            image_files = []
            for i, img in enumerate(images[:5]):  # 最多5张
                if 'data' in img:
                    # 保存临时文件
                    temp_path = os.path.join(self.log_dir, f'temp_img_{i}.jpg')
                    with open(temp_path, 'wb') as f:
                        f.write(img['data'])
                    image_files.append(temp_path)
            
            if image_files:
                file_input.set_input_files(image_files)
                time.sleep(3)  # 等待上传完成
                
                # 清理临时文件
                for f in image_files:
                    if os.path.exists(f):
                        os.remove(f)
            
        except Exception as e:
            self._log(f"图片上传失败: {e}", 'WARNING')
    
    def _fill_price(self, price: float):
        """填写价格"""
        try:
            price_input = self.page.locator('input[placeholder*="价格"], .product-price input')
            price_input.fill(str(price))
            time.sleep(0.5)
        except Exception as e:
            self._log(f"价格填写失败: {e}", 'WARNING')
    
    def _fill_stock(self, stock: int):
        """填写库存"""
        try:
            stock_input = self.page.locator('input[placeholder*="库存"], .product-stock input')
            stock_input.fill(str(stock))
            time.sleep(0.5)
        except Exception as e:
            self._log(f"库存填写失败: {e}", 'WARNING')
    
    def _fill_description(self, description: str):
        """填写商品详情"""
        try:
            # 切换到富文本编辑器
            editor = self.page.locator('.product-description-editor')
            if editor.count() > 0:
                editor.fill(description)
                time.sleep(0.5)
        except Exception as e:
            self._log(f"详情填写失败: {e}", 'WARNING')
    
    def _submit_product(self):
        """提交商品审核"""
        try:
            # 点击提交按钮
            submit_btn = self.page.locator('button:has-text("提交审核"), button:has-text("发布")')
            submit_btn.click()
            
            # 等待提交完成
            time.sleep(3)
            
            # 检查是否有错误提示
            error_msg = self.page.locator('.error-message, .ant-message-error')
            if error_msg.count() > 0:
                msg_text = error_msg.first.inner_text()
                raise Exception(f"提交失败: {msg_text}")
            
        except Exception as e:
            raise Exception(f"提交失败: {e}")
    
    def upload_products(self, products: List[Dict]):
        """批量上架商品"""
        total = len(products)
        self._log(f"开始批量上架，共 {total} 个商品")
        
        for i, product in enumerate(products):
            self._log(f"[{i+1}/{total}] 处理中...")
            
            success = False
            retries = self.config.get('upload', {}).get('retry', 3)
            
            for attempt in range(retries):
                try:
                    success = self.upload_product(product)
                    if success:
                        self.results['success'] += 1
                        break
                except Exception as e:
                    self._log(f"第{attempt+1}次尝试失败: {e}", 'ERROR')
                    time.sleep(2)
            
            if not success:
                self.results['failed'] += 1
                self.results['details'].append({
                    'title': product.get('title', ''),
                    'error': '多次尝试后仍失败',
                })
            
            # 延迟，避免操作过快
            delay = self.config.get('upload', {}).get('delay', 2)
            time.sleep(delay)
        
        self._log(f"批量上架完成: 成功 {self.results['success']} 个，失败 {self.results['failed']} 个")
    
    def close(self):
        """关闭浏览器"""
        if self.browser:
            self.browser.close()
            self._log("浏览器已关闭")


def main():
    parser = argparse.ArgumentParser(description='抖音小店自动上架')
    parser.add_argument('--input', required=True, help='商品数据文件')
    parser.add_argument('--config', help='配置文件')
    parser.add_argument('--log-dir', default='./logs', help='日志目录')
    
    args = parser.parse_args()
    
    # 加载商品数据
    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    products = data.get('products', [])
    print(f"加载 {len(products)} 个商品")
    
    if not products:
        print("没有商品需要上架")
        return
    
    # 创建上传器
    uploader = DouyinUploader(args.config, args.log_dir)
    
    try:
        # 启动浏览器
        uploader.start_browser()
        
        # 尝试加载cookie
        if not uploader._load_cookies():
            # 需要登录
            uploader.login()
        
        # 批量上架
        uploader.upload_products(products)
        
        # 输出结果
        print(f"\n上架结果:")
        print(f"  成功: {uploader.results['success']} 个")
        print(f"  失败: {uploader.results['failed']} 个")
        
    except KeyboardInterrupt:
        print("\n用户中断")
    finally:
        uploader.close()


if __name__ == '__main__':
    main()

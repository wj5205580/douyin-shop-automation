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
        
        log_file = os.path.join(self.log_dir, f'upload_{datetime.now().strftime("%Y%m%d")}.log')
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
    
    def start_browser(self):
        """启动浏览器"""
        self._log("启动浏览器...")
        
        playwright = sync_playwright().start()
        
        browser_config = self.config.get('qianfan', {})
        
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
        self._log("开始登录抖音小店...")
        
        config = self.config.get('qianfan', {})
        self.page.goto(config.get('login_url', 'https://fxg.jinritemai.com/'))
        
        # 等待登录页面加载
        self.page.wait_for_load_state('networkidle')
        
        # 抖音小店登录方式可能有多种：扫码/账号密码/手机号
        # 先等待用户手动登录或扫码
        
        self._log("请手动完成登录（支持扫码或账号密码），登录完成后按回车继续...")
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
        """上传单个商品到小红书"""
        try:
            self._log(f"开始上架: {product.get('title', '未知')[:30]}...")
            
            # 进入商品发布页面
            self.page.goto('https://fxg.jinritemai.com/app-system/goods/publish')
            self.page.wait_for_load_state('networkidle')
            
            # 等待页面加载
            time.sleep(2)
            
            # 1. 选择类目
            self._select_category(product.get('category_qianfan', ''))
            
            # 2. 填写商品标题（小红书标题要求更短，更侧重关键词）
            self._fill_title(product.get('title', ''))
            
            # 3. 填写商品描述/卖点
            self._fill_description(product.get('description', ''), product.get('title', ''))
            
            # 4. 上传主图和详情图
            self._upload_images(product.get('images_processed', []))
            
            # 5. 填写价格
            self._fill_price(product.get('price', 0))
            
            # 6. 填写库存
            self._fill_stock(product.get('stock', 999))
            
            # 7. 添加标签/话题
            self._add_tags(product.get('category', ''), product.get('title', ''))
            
            # 8. 提交审核
            self._submit_product()
            
            self._log(f"上架成功: {product.get('title', '未知')[:30]}...")
            return True
            
        except Exception as e:
            self._log(f"上架失败: {e}", 'ERROR')
            return False
    
    def _select_category(self, category_id: str):
        """选择商品类目"""
        try:
            # 点击类目选择
            self.page.click('.category-selector, [class*="category"], button:has-text("选择类目")')
            time.sleep(1)
            
            # 根据类目ID选择（小红书是三级类目）
            if category_id:
                # 搜索或选择类目
                search_input = self.page.locator('input[placeholder*="搜索类目"], .category-search input').first
                if search_input.count() > 0:
                    search_input.fill(category_id)
                    time.sleep(1)
                
                # 选择第一个匹配结果
                result = self.page.locator('.category-item, .category-result-item').first
                if result.count() > 0:
                    result.click()
                    time.sleep(1)
            
            # 确认选择
            confirm_btn = self.page.locator('button:has-text("确认"), button:has-text("确定"), .confirm-btn').first
            if confirm_btn.count() > 0:
                confirm_btn.click()
                time.sleep(1)
            
        except Exception as e:
            self._log(f"类目选择失败: {e}", 'WARNING')
    
    def _fill_title(self, title: str):
        """填写商品标题（小红书标题20字以内，要有关键词）"""
        try:
            # 小红书标题通常限制20字
            if len(title) > 20:
                title = title[:17] + '...'
            
            # 查找标题输入框
            title_input = self.page.locator(
                'input[placeholder*="标题"], '
                'input[name="title"], '
                '.goods-title input, '
                '[class*="title"] input'
            ).first
            
            if title_input.count() > 0:
                title_input.fill(title)
                time.sleep(0.5)
            else:
                # 尝试其他选择器
                self.page.fill('.publish-form input[type="text"]:nth-child(1)', title)
                
        except Exception as e:
            self._log(f"标题填写失败: {e}", 'WARNING')
    
    def _fill_description(self, description: str, title: str):
        """填写商品描述/卖点（小红书侧重种草文案）"""
        try:
            # 如果没有描述，用标题生成
            if not description:
                description = f"✨{title}✨\n\n🔥爆款推荐\n💕品质保证\n📦快速发货"
            
            # 查找描述输入框（可能是textarea或富文本编辑器）
            desc_input = self.page.locator(
                'textarea[placeholder*="描述"], '
                'textarea[placeholder*="卖点"], '
                '.goods-desc textarea, '
                '[class*="description"] textarea, '
                '[class*="detail"] .editor'
            ).first
            
            if desc_input.count() > 0:
                desc_input.fill(description)
                time.sleep(0.5)
            
        except Exception as e:
            self._log(f"描述填写失败: {e}", 'WARNING')
    
    def _upload_images(self, images: List):
        """上传商品图片"""
        try:
            if not images:
                self._log("没有图片需要上传", 'WARNING')
                return
            
            # 小红书要求：
            # - 主图：1张，1:1或3:4
            # - 详情图：多张
            
            # 上传主图
            main_image_input = self.page.locator(
                'input[type="file"][accept*="image"], '
                '.main-image-upload input[type="file"], '
                '[class*="mainImage"] input[type="file"]'
            ).first
            
            if main_image_input.count() > 0 and images:
                # 处理第一张为主图
                img = images[0]
                if 'data' in img:
                    temp_path = os.path.join(self.log_dir, 'temp_main.jpg')
                    with open(temp_path, 'wb') as f:
                        f.write(img['data'])
                    main_image_input.set_input_files(temp_path)
                    time.sleep(2)
                    os.remove(temp_path)
            
            # 上传详情图
            detail_image_input = self.page.locator(
                '.detail-images input[type="file"], '
                '[class*="detailImage"] input[type="file"], '
                '.image-upload input[type="file"]'
            ).first
            
            if detail_image_input.count() > 0 and len(images) > 1:
                detail_images = images[1:6]  # 最多5张详情图
                image_files = []
                
                for i, img in enumerate(detail_images):
                    if 'data' in img:
                        temp_path = os.path.join(self.log_dir, f'temp_detail_{i}.jpg')
                        with open(temp_path, 'wb') as f:
                            f.write(img['data'])
                        image_files.append(temp_path)
                
                if image_files:
                    detail_image_input.set_input_files(image_files)
                    time.sleep(3)
                    
                    # 清理临时文件
                    for f in image_files:
                        if os.path.exists(f):
                            os.remove(f)
            
        except Exception as e:
            self._log(f"图片上传失败: {e}", 'WARNING')
    
    def _fill_price(self, price: float):
        """填写价格"""
        try:
            price_input = self.page.locator(
                'input[placeholder*="价格"], '
                'input[name="price"], '
                '.goods-price input'
            ).first
            
            if price_input.count() > 0:
                price_input.fill(str(price))
                time.sleep(0.5)
            
        except Exception as e:
            self._log(f"价格填写失败: {e}", 'WARNING')
    
    def _fill_stock(self, stock: int):
        """填写库存"""
        try:
            stock_input = self.page.locator(
                'input[placeholder*="库存"], '
                'input[name="stock"], '
                '.goods-stock input'
            ).first
            
            if stock_input.count() > 0:
                stock_input.fill(str(stock))
                time.sleep(0.5)
            
        except Exception as e:
            self._log(f"库存填写失败: {e}", 'WARNING')
    
    def _add_tags(self, category: str, title: str):
        """添加标签/话题（小红书特有）"""
        try:
            # 从配置获取标签
            tags_map = self.config.get('processing', {}).get('tags_map', {})
            tags = tags_map.get(category, ['好物推荐', '种草'])
            
            # 查找标签输入框
            tag_input = self.page.locator(
                'input[placeholder*="标签"], '
                'input[placeholder*="话题"], '
                '.tag-input input, '
                '[class*="tag"] input'
            ).first
            
            if tag_input.count() > 0:
                for tag in tags[:3]:  # 最多3个标签
                    tag_input.fill(tag)
                    time.sleep(0.3)
                    # 选择下拉框中的第一个
                    dropdown_item = self.page.locator('.tag-dropdown-item, .tag-suggestion').first
                    if dropdown_item.count() > 0:
                        dropdown_item.click()
                        time.sleep(0.3)
                    else:
                        tag_input.press('Enter')
                        time.sleep(0.3)
            
        except Exception as e:
            self._log(f"标签添加失败: {e}", 'WARNING')
    
    def _submit_product(self):
        """提交商品审核"""
        try:
            # 小红书通常是"立即上架"或"提交审核"
            submit_btn = self.page.locator(
                'button:has-text("立即上架"), '
                'button:has-text("提交审核"), '
                'button:has-text("发布"), '
                '.submit-btn, '
                '[class*="submit"] button'
            ).first
            
            if submit_btn.count() > 0:
                submit_btn.click()
                time.sleep(3)
            
            # 检查是否有错误提示
            error_msg = self.page.locator(
                '.error-message, '
                '.ant-message-error, '
                '[class*="error"]'
            ).first
            
            if error_msg.count() > 0 and error_msg.is_visible():
                msg_text = error_msg.inner_text()
                raise Exception(f"提交失败: {msg_text}")
            
            # 等待成功提示
            time.sleep(2)
            
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

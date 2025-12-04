"""
数据抓取模块 - 百度新闻搜索
"""
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re
from typing import List, Dict, Optional
import time
import random


class BaiduNewsCrawler:
    """百度新闻搜索爬虫"""
    
    def __init__(self):
        self.base_url = "https://www.baidu.com/s?tn=news"
        
        # Selenium配置
        from selenium.webdriver.chrome.options import Options
        from selenium import webdriver
        
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')  # 无头模式
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--window-size=1920x1080')
        
        # 随机User-Agent
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.97 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5790.170 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/116.0.1938.69 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.97 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15',
        ]
        
        self.chrome_options.add_argument(f'--user-agent={random.choice(self.user_agents)}')
        
        # 初始化浏览器
        try:
            self.driver = webdriver.Chrome(options=self.chrome_options)
        except Exception as e:
            print(f"浏览器初始化失败: {str(e)}")
            self.driver = None
    
    def search(self, keyword: str, max_results: int = 10) -> List[Dict]:
        """
        搜索新闻
        
        Args:
            keyword: 搜索关键字
            max_results: 最大返回结果数
            
        Returns:
            新闻列表，每个新闻包含：title, summary, cover, url, source
        """
        if not self.driver:
            print("浏览器未初始化，无法抓取数据")
            return []
            
        try:
            # 添加随机延迟，降低请求频率（1-3秒）
            time.sleep(random.uniform(1, 3))
            
            # 直接构造搜索URL
            search_url = f"https://www.baidu.com/s?tn=news&word={urllib.parse.quote(keyword)}"
            self.driver.get(search_url)
            
            # 等待搜索结果加载
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.common.by import By
            
            WebDriverWait(self.driver, 15).until(
                lambda driver: driver.find_elements(By.CSS_SELECTOR, '.result') or \
                               driver.find_elements(By.CSS_SELECTOR, '.c-container')
            )
            
            # 获取页面源代码
            page_source = self.driver.page_source
            
            # 解析HTML
            soup = BeautifulSoup(page_source, 'html.parser')
            
            news_list = []
            
            # 尝试多种方法查找新闻容器
            news_containers = soup.find_all('div', class_='result') or \
                              soup.find_all('div', class_='c-container') or \
                              soup.find_all('div', class_=re.compile(r'news|content'))
            
            for container in news_containers:
                if len(news_list) >= max_results:
                    break
                
                # 查找标题和链接
                title_elem = container.find('h3')
                if not title_elem:
                    continue
                
                title_link = title_elem.find('a', href=True)
                if not title_link:
                    continue
                
                title_text = title_link.get_text(strip=True)
                if len(title_text) < 5:
                    continue
                
                # 查找来源和时间
                source_time = container.find('p', class_='c-author') or \
                             container.find('span', class_='c-author') or \
                             container.find('div', class_='c-author')
                source = ''
                if source_time:
                    source_text = source_time.get_text(strip=True)
                    # 分离来源和时间
                    if ' ' in source_text:
                        source = source_text.split(' ')[0]
                    elif '·' in source_text:
                        source = source_text.split('·')[0]
                    else:
                        source = source_text
                
                # 查找摘要
                summary = ''
                summary_elem = container.find('div', class_='c-summary') or \
                               container.find('span', class_='c-summary') or \
                               container.find('div', class_='content')
                if summary_elem:
                    summary = summary_elem.get_text(strip=True)
                
                # 查找封面图片
                cover = ''
                img_elem = container.find('img')
                if img_elem:
                    cover = img_elem.get('src') or img_elem.get('data-src') or ''
                    if cover.startswith('//'):
                        cover = 'https:' + cover
                
                # 构建新闻项
                news_item = {
                    'title': title_text,
                    'url': title_link['href'],
                    'source': source,
                    'summary': summary,
                    'cover': cover
                }
                
                # 检查是否重复
                if not any(n.get('title') == news_item.get('title') for n in news_list):
                    news_list.append(news_item)
            
            return news_list
            
        except Exception as e:
            print(f"抓取错误: {str(e)}")
            return []
    
    
    def _parse_news_item_from_container(self, container, title_text: str, link) -> Optional[Dict]:
        """从容器中解析单个新闻项"""
        try:
            news = {}
            
            # 1. 标题
            if not title_text:
                return None
            
            news['title'] = title_text
            
            # 2. URL
            href = link.get('href', '')
            if href.startswith('//'):
                href = 'https:' + href
            elif href.startswith('/'):
                href = 'https://www.baidu.com' + href
            
            # 处理百度跳转链接
            if 'baidu.com/link' in href or '/link?url=' in href:
                try:
                    from urllib.parse import parse_qs, urlparse, unquote
                    parsed = urlparse(href)
                    query_params = parse_qs(parsed.query)
                    if 'url' in query_params:
                        real_url = unquote(query_params['url'][0])
                        news['url'] = real_url
                    else:
                        news['url'] = href
                except:
                    news['url'] = href
            else:
                news['url'] = href
            
            # 3. 概要 - 查找摘要信息
            summary = self._extract_summary(container, title_text)
            news['summary'] = summary
            
            # 4. 封面图片
            cover = self._extract_cover(container)
            news['cover'] = cover
            
            # 5. 来源
            source = self._extract_source(container)
            news['source'] = source
            
            # 确保所有字段都存在
            news.setdefault('title', '')
            news.setdefault('summary', '')
            news.setdefault('cover', '')
            news.setdefault('url', '')
            news.setdefault('source', '')
            
            # 只要有标题和URL就返回
            if news.get('title') and len(news.get('title', '')) >= 5 and news.get('url'):
                return news
            
            return None
            
        except Exception as e:
            print(f"解析新闻项错误: {str(e)}")
            return None
    

    
    def _extract_cover(self, container) -> str:
        """提取封面图片"""
        try:
            # 查找图片
            img_elem = container.find('img')
            if img_elem:
                img_src = img_elem.get('src') or img_elem.get('data-src') or img_elem.get('data-original')
                if img_src:
                    if img_src.startswith('//'):
                        img_src = 'https:' + img_src
                    elif img_src.startswith('/'):
                        img_src = 'https://www.baidu.com' + img_src
                    
                    # 过滤掉百度的小图标和logo
                    if 'baidu.com' in img_src:
                        if any(keyword in img_src.lower() for keyword in ['icon', 'logo', 'static']):
                            return ''
                    
                    return img_src
            return ''
        except:
            return ''
    



def crawl_news(keyword: str, max_results: int = 10) -> List[Dict]:
    """
    抓取新闻的便捷函数
    
    Args:
        keyword: 搜索关键字
        max_results: 最大返回结果数
        
    Returns:
        新闻列表
    """
    crawler = BaiduNewsCrawler()
    return crawler.search(keyword, max_results)

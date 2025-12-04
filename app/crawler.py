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
        # 尝试使用不同的百度新闻搜索URL
        self.base_urls = [
            "https://news.baidu.com/ns",
            "https://www.baidu.com/s?tn=news",
            "https://www.baidu.com/news"
        ]
        
        # 随机User-Agent列表，避免被百度识别为爬虫
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.97 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5790.170 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/116.0.1938.69 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.97 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15',
        ]
        
        # 更简单的请求头，减少被识别为爬虫的概率
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Host': 'www.baidu.com',
            'Referer': 'https://www.baidu.com/',
            'Upgrade-Insecure-Requests': '1',
        }
        
        self.session = requests.Session()
        
        # 设置会话的超时时间和重试次数
        from requests.adapters import HTTPAdapter
        from requests.packages.urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount('https://', adapter)
        self.session.mount('http://', adapter)
        
        # 随机选择User-Agent和请求头
        self._update_session_headers()
    
    def _update_session_headers(self):
        """更新会话的请求头和User-Agent"""
        self.session.headers.clear()
        self.session.headers.update(self.headers)
        
        # 随机选择User-Agent
        self.session.headers['User-Agent'] = random.choice(self.user_agents)
        
        # 随机选择Host和Referer（根据URL选择）
        random_url = random.choice(self.base_urls)
        if 'news.baidu.com' in random_url:
            self.session.headers['Host'] = 'news.baidu.com'
            self.session.headers['Referer'] = 'https://news.baidu.com/'
        else:
            self.session.headers['Host'] = 'www.baidu.com'
            self.session.headers['Referer'] = 'https://www.baidu.com/'
        
        return random_url
    
    def search(self, keyword: str, max_results: int = 10) -> List[Dict]:
        """
        搜索新闻
        
        Args:
            keyword: 搜索关键字
            max_results: 最大返回结果数
            
        Returns:
            新闻列表，每个新闻包含：title, summary, cover, url, source
        """
        try:
            # 添加随机延迟，降低请求频率（1-3秒）
            time.sleep(random.uniform(1, 3))
            
            # 随机选择一个URL
            current_url = self._update_session_headers()
            
            # 构建请求参数
            if 'news.baidu.com/ns' in current_url:
                params = {
                    'word': keyword,
                    'pn': '0',
                    'rn': str(max_results),
                    'tn': 'news'
                }
            else:
                params = {
                    'wd': keyword,
                    'pn': '0',
                    'rn': str(max_results),
                    'tn': 'news'
                }
            
            # 发送请求，增加超时时间
            response = self.session.get(current_url, params=params, timeout=30)
            
            # 解决中文乱码问题
            if response.encoding == 'ISO-8859-1':
                response.encoding = 'utf-8'
            else:
                response.encoding = response.apparent_encoding
            
            if response.status_code != 200:
                print(f"请求失败，状态码: {response.status_code}，URL: {current_url}")
                
                # 如果第一个URL失败，尝试其他URL
                for backup_url in self.base_urls:
                    if backup_url == current_url:
                        continue
                    
                    time.sleep(random.uniform(0.5, 1))
                    
                    # 构建备份URL的参数
                    if 'news.baidu.com/ns' in backup_url:
                        backup_params = {
                            'word': keyword,
                            'pn': '0',
                            'rn': str(max_results),
                            'tn': 'news'
                        }
                    else:
                        backup_params = {
                            'wd': keyword,
                            'pn': '0',
                            'rn': str(max_results),
                            'tn': 'news'
                        }
                    
                    backup_response = self.session.get(backup_url, params=backup_params, timeout=30)
                    
                    if backup_response.status_code == 200:
                        print(f"备份URL成功: {backup_url}")
                        response = backup_response
                        break
                    else:
                        print(f"备份URL也失败了，状态码: {backup_response.status_code}，URL: {backup_url}")
                
                if response.status_code != 200:
                    return []
            
            # 解析HTML - 优先使用html.parser（更兼容）
            soup = BeautifulSoup(response.text, 'html.parser')
            
            news_list = []
            
            # 尝试最简单的方法：直接提取所有a标签的文本和链接
            all_links = soup.find_all('a', href=True)
            
            for link in all_links:
                if len(news_list) >= max_results:
                    break
                
                # 查找标题文本
                title_text = link.get_text(strip=True)
                # 过滤掉太短的标题
                if len(title_text) < 10:
                    continue
                
                # 构建基本的新闻项
                news_item = {
                    'title': title_text,
                    'url': link['href'],
                    'source': '',
                    'summary': '',
                    'cover': ''
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

    def _extract_summary(self, container, title_text: str) -> str:
        """提取摘要"""
        try:
            # 方法1: 查找h3后面的兄弟元素（摘要通常在标题后面）
            current = container
            # 如果container就是h3，查找它的父容器
            if container.name == 'h3':
                current = container.find_parent('div') or container
            
            # 查找摘要span或div
            summary_elem = current.find('span', class_=re.compile(r'content|abstract|summary|desc|c-abstract|c-span9')) or \
                          current.find('div', class_=re.compile(r'content|abstract|summary|desc|c-abstract'))
            
            if summary_elem:
                summary_text = summary_elem.get_text(strip=True)
                # 移除标题
                summary_text = summary_text.replace(title_text, '').strip()
                # 移除来源和时间
                summary_text = re.sub(r'来源[：:].*', '', summary_text).strip()
                summary_text = re.sub(r'\d{4}[-/\d{1,2}[-/\d{1,2}.*', '', summary_text).strip()
                if len(summary_text) > 10:
                    return summary_text[:300]
            
            # 方法2: 从容器文本中提取
            container_text = current.get_text(strip=True)
            if len(container_text) > len(title_text) + 20:
                # 移除标题
                summary = container_text.replace(title_text, '').strip()
                # 移除来源和时间信息
                summary = re.sub(r'来源[：:].*', '', summary).strip()
                summary = re.sub(r'\d{4}[-/\d{1,2}[-/\d{1,2}.*', '', summary).strip()
                # 移除URL
                summary = re.sub(r'https?://[^\s]+', '', summary).strip()
                # 移除多余的空白
                summary = re.sub(r'\s+', ' ', summary).strip()
                if len(summary) > 20:
                    return summary[:300]
            
            return ''
        except Exception as e:
            return ''

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

    def _extract_source(self, container) -> str:
        """提取来源"""
        try:
            # 方法1: 查找来源标签
            source_elem = container.find('span', class_=re.compile(r'source|author|site|from|c-author|c-color-gray')) or \
                         container.find('div', class_=re.compile(r'source|author|site|from|c-author')) or \
                         container.find('a', class_=re.compile(r'source|site'))
            
            if source_elem:
                source_text = source_elem.get_text(strip=True)
                # 移除时间信息
                source_text = re.sub(r'\s+\d{4}[-/\d{1,2}[-/\d{1,2}.*', '', source_text).strip()
                if source_text and len(source_text) < 50:
                    return source_text
            
            # 方法2: 从文本中提取
            container_text = container.get_text()
            # 查找"来源：xxx"模式
            source_match = re.search(r'来源[：:]\s*([^\s\n]+)', container_text)
            if source_match:
                return source_match.group(1).strip()[:50]
            
            # 查找"xxx 2024-01-01"模式（来源+时间）
            source_match = re.search(r'([^\s]+)\s+\d{4}[-/\d{1,2}[-/\d{1,2}', container_text)
            if source_match:
                source_text = source_match.group(1).strip()
                # 过滤掉明显不是来源的词
                if source_text and len(source_text) < 30 and '来源' not in source_text:
                    return source_text[:50]
            
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

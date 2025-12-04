"""直接测试解析"""
import requests
from bs4 import BeautifulSoup
from app.crawler import BaiduNewsCrawler

crawler = BaiduNewsCrawler()

keyword = "西昌"
url = "https://www.baidu.com/s"
params = {
    'rtt': '1',
    'bsst': '1',
    'cl': '2',
    'tn': 'news',
    'rsv_dl': 'ns_pc',
    'word': keyword
}

response = requests.get(url, params=params, headers=crawler.headers, timeout=10)
response.encoding = 'utf-8'

soup = BeautifulSoup(response.text, 'lxml')
h3_list = soup.find_all('h3')

print(f"找到 {len(h3_list)} 个h3标签\n")

count = 0
for i, h3 in enumerate(h3_list[:10], 1):
    link = h3.find('a', href=True)
    if link:
        title_text = link.get_text(strip=True)
        
        if len(title_text) < 3:
            continue
        
        nav_keywords = ['百度', '新闻', '网页', '贴吧', '知道', '图片', '视频', '地图', '文库', '更多', '设置']
        if title_text in nav_keywords or any(keyword in title_text for keyword in ['百度一下', '搜索', '登录']):
            continue
        
        parent = h3.find_parent('div')
        if not parent:
            parent = h3.find_parent()
        
        if parent:
            print(f"{i}. 标题: {title_text[:50]}")
            news_item = crawler._parse_news_item(h3, link, parent)
            if news_item:
                print(f"   -> 解析成功!")
                print(f"   标题: {news_item.get('title', '')[:50]}")
                print(f"   概要: {news_item.get('summary', '')[:60]}")
                print(f"   来源: {news_item.get('source', '')}")
                print(f"   URL: {news_item.get('url', '')[:60]}")
                count += 1
            else:
                print(f"   -> 解析返回None")
            print()

print(f"\n成功解析: {count} 条")


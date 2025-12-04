"""测试解析方法"""
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

soup = BeautifulSoup(response.text, 'html.parser')
h3_list = soup.find_all('h3')

print(f"找到 {len(h3_list)} 个h3标签\n")

for i, h3 in enumerate(h3_list[:5], 1):
    link = h3.find('a', href=True)
    if link:
        title_text = link.get_text(strip=True)
        print(f"{i}. 标题: {title_text}")
        print(f"   长度: {len(title_text)}")
        
        if len(title_text) < 3:
            print("   -> 标题太短，跳过")
            continue
        
        if title_text in ['百度', '新闻', '网页', '贴吧', '知道', '图片', '视频', '地图', '文库', '更多']:
            print("   -> 是导航链接，跳过")
            continue
        
        parent = h3.find_parent('div')
        if parent:
            print(f"   找到父容器")
            news_item = crawler._parse_news_item(h3, link, parent)
            if news_item:
                print(f"   -> 解析成功!")
                print(f"   标题: {news_item.get('title', '')[:50]}")
                print(f"   概要: {news_item.get('summary', '')[:50]}")
                print(f"   来源: {news_item.get('source', '')}")
            else:
                print(f"   -> 解析返回None")
        else:
            print(f"   未找到父容器")


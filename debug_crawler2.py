"""调试爬虫 - 查看解析过程"""
import requests
from bs4 import BeautifulSoup
import re

def debug_search():
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
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.97 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    
    response = requests.get(url, params=params, headers=headers, timeout=10)
    response.encoding = 'utf-8'
    
    print(f"状态码: {response.status_code}")
    print(f"内容长度: {len(response.text)}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 查找h3
    h3_list = soup.find_all('h3')
    print(f"\n找到 {len(h3_list)} 个h3标签")
    
    count = 0
    for i, h3 in enumerate(h3_list[:10], 1):
        link = h3.find('a', href=True)
        if link:
            title = link.get_text(strip=True)
            href = link.get('href', '')
            print(f"\n{i}. 标题: {title[:50]}")
            print(f"   URL: {href[:80]}")
            
            # 查找父容器
            parent = h3.find_parent('div')
            if parent:
                parent_text = parent.get_text(strip=True)
                print(f"   父容器文本长度: {len(parent_text)}")
                print(f"   父容器文本前100字: {parent_text[:100]}")
                count += 1
            else:
                print(f"   未找到父容器")
    
    print(f"\n有父容器的h3数量: {count}")

if __name__ == '__main__':
    debug_search()


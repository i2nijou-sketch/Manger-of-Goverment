"""
调试爬虫 - 查看实际返回的HTML
"""
import requests
from bs4 import BeautifulSoup
import urllib.parse

def debug_baidu_search():
    """调试百度搜索"""
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
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        print(f"状态码: {response.status_code}")
        print(f"URL: {response.url}")
        print(f"内容长度: {len(response.text)}")
        
        # 保存HTML到文件
        with open('baidu_result.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("HTML已保存到 baidu_result.html")
        
        # 解析HTML
        soup = BeautifulSoup(response.text, 'lxml')
        
        # 查找所有h3标签
        h3_list = soup.find_all('h3')
        print(f"\n找到 {len(h3_list)} 个h3标签")
        for i, h3 in enumerate(h3_list[:5], 1):
            print(f"{i}. {h3.get_text(strip=True)[:50]}")
        
        # 查找所有包含baidu.com/link的链接
        links = soup.find_all('a', href=re.compile(r'baidu\.com/link'))
        print(f"\n找到 {len(links)} 个百度链接")
        for i, link in enumerate(links[:5], 1):
            print(f"{i}. {link.get_text(strip=True)[:50]} -> {link.get('href', '')[:80]}")
        
    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    import re
    debug_baidu_search()


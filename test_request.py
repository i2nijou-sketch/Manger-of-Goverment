#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试网络请求和页面解析
"""

import requests
from bs4 import BeautifulSoup


def test_baidu_news_request():
    """测试百度新闻页面请求和解析"""
    print("开始测试百度新闻页面请求和解析...")
    
    # 设置请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.97 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Host': 'www.baidu.com',
        'Pragma': 'no-cache',
        'Referer': 'https://www.baidu.com/',
    }
    
    # 测试URL
    url = 'https://www.baidu.com/s?tn=news&word=人工智能'
    
    try:
        # 发送请求
        response = requests.get(url, headers=headers, timeout=15)
        
        print(f"\n请求状态码: {response.status_code}")
        print(f"响应内容长度: {len(response.text)} 字符")
        
        # 检查响应内容
        if response.status_code == 200:
            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找h3标签
            h3_list = soup.find_all('h3')
            print(f"找到的h3标签数量: {len(h3_list)}")
            
            # 打印前3个h3标签的内容
            for i, h3 in enumerate(h3_list[:3], 1):
                print(f"第 {i} 个h3标签: {h3.get_text(strip=True)}")
                
                # 查找链接
                link = h3.find('a', href=True)
                if link:
                    print(f"  链接: {link['href']}")
            
            # 检查是否有新闻内容
            if '百度新闻' in response.text:
                print("\n✓ 响应包含百度新闻内容")
            else:
                print("\n✗ 响应不包含百度新闻内容")
            
            # 检查是否有反爬机制
            if '验证码' in response.text or '请输入验证码' in response.text:
                print("✗ 检测到验证码，可能触发了反爬机制")
            elif '访问过于频繁' in response.text or '请稍后再试' in response.text:
                print("✗ 检测到访问过于频繁的提示")
            else:
                print("✓ 未检测到反爬机制的提示")
            
        else:
            print(f"✗ 请求失败，状态码: {response.status_code}")
            
    except Exception as e:
        print(f"✗ 请求过程中出现错误: {str(e)}")


if __name__ == "__main__":
    test_baidu_news_request()
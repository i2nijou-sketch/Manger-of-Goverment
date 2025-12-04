"""简单测试爬虫"""
from app.crawler import crawl_news

print("开始测试爬虫...")
print("关键字: 西昌")
print("最大结果数: 5")
print("-" * 60)

results = crawl_news('西昌', 5)

print(f"\n抓取结果: 共 {len(results)} 条数据")
print("-" * 60)

for i, news in enumerate(results, 1):
    print(f"\n[{i}]")
    print(f"标题: {news.get('title', '无标题')}")
    print(f"概要: {news.get('summary', '无概要')[:80]}...")
    print(f"来源: {news.get('source', '未知')}")
    print(f"URL: {news.get('url', '无URL')[:60]}...")
    if news.get('cover'):
        print(f"封面: {news.get('cover', '无封面')[:60]}...")


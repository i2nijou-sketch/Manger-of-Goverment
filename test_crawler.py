"""
测试数据抓取模块
"""
from app.crawler import crawl_news

def test_crawler():
    """测试爬虫功能"""
    print("=" * 60)
    print("数据抓取模块测试")
    print("=" * 60)
    
    # 测试关键字
    keyword = "西昌"
    print(f"\n测试关键字: {keyword}")
    print("开始抓取...")
    
    try:
        results = crawl_news(keyword, max_results=5)
        
        print(f"\n抓取结果: 共 {len(results)} 条")
        print("-" * 60)
        
        for i, news in enumerate(results, 1):
            print(f"\n[{i}] 标题: {news.get('title', '无标题')}")
            print(f"    概要: {news.get('summary', '无概要')[:100]}...")
            print(f"    来源: {news.get('source', '未知')}")
            print(f"    URL: {news.get('url', '无URL')[:80]}...")
            if news.get('cover'):
                print(f"    封面: {news.get('cover', '无封面')[:80]}...")
            print("-" * 60)
        
        if len(results) > 0:
            print("\n✓ 测试通过！数据抓取功能正常")
            return True
        else:
            print("\n⚠ 未抓取到数据，可能是网络问题或页面结构变化")
            return False
            
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_crawler()


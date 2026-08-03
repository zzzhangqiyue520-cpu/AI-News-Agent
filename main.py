from src.news_manager import NewsManager
from src.crawler import crawl
from src.parser import parse

def main():
    print("AI-News-Agent启动")

    # 1.创建管理器
    manager = NewsManager(
        "data/news.json"
    )

    #2. 获取网页
    html = crawl()

    #3.解析新闻
    news_list = parse(html)

    print("获取新闻数量：",len(news_list))

    #4.保存新闻
    manager.save_news(news_list)

    #5.读取测试
    news = manager.load_news()

    for item in news:
        print("-----------------")
        print(item["title"])
        print(item["url"])

if __name__ == "__main__":
    main()


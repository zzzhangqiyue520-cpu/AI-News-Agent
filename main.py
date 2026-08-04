import asyncio

from src.news_manager import NewsManager
from src.crawler import crawl
from src.parser import parse

async def main():
    print("AI-News-Agent启动")

    # 1.创建管理器
    manager = NewsManager(
        "data/news.json"
    )

    #2. 异步爬取
    html_list = await crawl()

    news_list = []

    #3.多个网页分别解析
    for html in html_list:

        if html:

            news = parse(html)

            news_list.append(news)

    print("获取新闻数量：",len(news_list))

    manager.save_news(news_list)

    news = manager.load_news()

    for item in news:

        print("-------------------------")

        print(item["title"])
        print(item["url"])
        print(item["time"])

if __name__ == "__main__":
    asyncio.run(main())


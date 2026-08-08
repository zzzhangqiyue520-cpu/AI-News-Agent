import asyncio

from src.news_manager import NewsManager
from src.crawler import crawl

from src.parser.deepmind import parse_deepmind
from src.parser.anthropic import parse_anthropic

from src.ai.analyzer import summarize


async def main():

    print("AI-News-Agent启动")

    # 1.创建管理器
    manager = NewsManager(
        "data/news.json"
    )

    # 2.异步爬取
    html_list = await crawl()

    news_list = []


    # 3.根据来源选择解析器
    for item in html_list:

        if item["source"] == "DeepMind":

            news = parse_deepmind(
                item["html"]
            )

        elif item["source"] == "Anthropic":

            news = parse_anthropic(
                item["html"]
            )

        else:

            print(
                "未知来源:",
                item["source"]
            )

            continue

        news_list.extend(news)

    print(
        "获取新闻数量:",
        len(news_list)
    )

    # 4.保存新闻
    manager.save_news(news_list)

    # 5.读取新闻并调用AI分析
    news = manager.load_news()

    for item in news:

        print("-------------------------")

        print("标题:")
        print(item["title"])


        print("链接:")
        print(item["url"])


        print("来源:")
        print(item["source"])


        print("时间:")
        print(item["time"])

        result = summarize(item)

        print("\nAI分析结果:")
        print(result)

if __name__ == "__main__":

    asyncio.run(main())
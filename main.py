import asyncio
import json


from src.sources.deepmind.crawler import (
    DeepMindCrawler
)


from src.sources.deepmind.detail import (
    DeepMindDetail
)


from src.sources.deepmind.parser import (
    parse_news
)



async def main():


    crawler = DeepMindCrawler()

    detail = DeepMindDetail()



    print(
        "开始获取新闻列表..."
    )


    news_list = await crawler.crawl()



    print(
        "发现",
        len(news_list),
        "条新闻"
    )



    results = []



    for news in news_list[:5]:


        print(
            "正在处理:",
            news["title"]
        )



        try:

            content = await detail.parse_content(
                news["url"]
            )


        except Exception as e:


            print(
                "文章解析失败:",
                e
            )


            content = ""



        news["content"] = content



        data = parse_news(
            news
        )


        results.append(
            data
        )



    with open(
        "data/news.json",
        "w",
        encoding="utf-8"
    ) as f:


        json.dump(
            results,
            f,
            ensure_ascii=False,
            indent=4
        )



    print(
        "完成，保存 deepmind_news.json"
    )



if __name__ == "__main__":


    asyncio.run(
        main()
    )
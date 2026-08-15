# src/sources/deepmind/source.py

from src.sources.base import BaseSource

from src.sources.deepmind.crawler import (
    DeepMindCrawler
)

from src.sources.deepmind.detail import (
    DeepMindDetail
)


class DeepMindSource(BaseSource):
    """
    DeepMind 新闻源。

    内部：
        crawler.py 负责新闻列表
        detail.py 负责文章正文

    对外：
        fetch()
    """

    def __init__(self):

        self.crawler = DeepMindCrawler()

        self.detail = DeepMindDetail()

        self.name = "DeepMind"


    async def fetch(self):

        print(
            "\n开始获取 DeepMind 新闻..."
        )


        news_list = await self.crawler.crawl()


        print(
            f"发现 {len(news_list)} 条 DeepMind 新闻"
        )


        results = []


        for news in news_list:

            print(
                "正在获取:",
                news["title"]
            )


            try:

                content = await self.detail.parse_content(
                    news["url"]
                )


                news["content"] = content


            except Exception as e:

                print(
                    "DeepMind 正文获取失败:",
                    e
                )


                news["content"] = ""


            news["source"] = self.name


            results.append(
                news
            )


        return results
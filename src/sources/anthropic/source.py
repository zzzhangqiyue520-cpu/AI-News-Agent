# src/sources/anthropic/source.py

from src.sources.base import BaseSource

from src.sources.anthropic.crawler import (
    fetch_rss
)

from src.sources.anthropic.parser import (
    parse_rss
)


class AnthropicSource(BaseSource):
    """
    Anthropic 新闻源。

    Anthropic 当前通过 RSS 获取数据，
    因此不需要单独请求详情页面。

    对外统一提供：
        fetch()
    """

    def __init__(self):

        self.name = "Anthropic"


    async def fetch(self):

        print(
            "\n开始获取 Anthropic 新闻..."
        )


        try:

            xml = await fetch_rss()


            news_list = parse_rss(
                xml
            )


            print(
                f"发现 {len(news_list)} 条 Anthropic 新闻"
            )


            return news_list


        except Exception as e:

            print(
                "Anthropic 获取失败:",
                e
            )


            return []
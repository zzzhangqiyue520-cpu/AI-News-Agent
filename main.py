import asyncio
import json

from pathlib import Path

from src.ai.analyzer import summarize

# DeepMind
from src.sources.deepmind.crawler import DeepMindCrawler
from src.sources.deepmind.detail import DeepMindDetail

# Anthropic
from src.sources.anthropic.crawler import fetch_rss
from src.sources.anthropic.parser import parse_rss


DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = DATA_DIR / "news.json"


async def get_deepmind_news():

    print("\n开始获取 DeepMind 新闻...")

    crawler = DeepMindCrawler()

    news_list = await crawler.crawl()

    print(
        f"发现 {len(news_list)} 条 DeepMind 新闻"
    )

    detail_parser = DeepMindDetail()

    results = []

    for news in news_list:

        print(
            "正在获取:",
            news["title"]
        )

        try:

            content = await detail_parser.parse_content(
                news["url"]
            )

            news["content"] = content

        except Exception as e:

            print(
                "正文获取失败:",
                e
            )

            news["content"] = ""

        news["source"] = "DeepMind"

        results.append(news)

    return results


async def get_anthropic_news():

    print("\n开始获取 Anthropic 新闻...")

    try:

        xml = await fetch_rss()

        news_list = parse_rss(xml)

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


async def main():

    print(
        "====== AI News Agent ======"
    )


    # ==========================
    # 1. 获取新闻
    # ==========================

    deepmind_news = await get_deepmind_news()

    anthropic_news = await get_anthropic_news()


    all_news = []

    all_news.extend(
        deepmind_news
    )

    all_news.extend(
        anthropic_news
    )


    print(
        f"\n总新闻数量: {len(all_news)}"
    )


    # ==========================
    # 2. AI分析
    # ==========================

    print(
        "\n开始 AI 新闻分析..."
    )


    for news in all_news:

        print(
            "\n正在分析:",
            news["title"]
        )


        # 如果没有正文，不调用AI
        if not news.get("content"):

            print(
                "没有正文，跳过 AI 分析"
            )

            news["analysis"] = {
                "summary": "",
                "keywords": [],
                "category": "其他"
            }

            continue


        try:

            analysis = summarize(
                news
            )

            news["analysis"] = analysis


            print(
                "AI分析完成"
            )


        except Exception as e:

            print(
                "AI分析失败:",
                e
            )

            news["analysis"] = {
                "summary": "",
                "keywords": [],
                "category": "其他"
            }


    # ==========================
    # 3. 保存
    # ==========================

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            all_news,
            f,
            ensure_ascii=False,
            indent=4
        )


    print(
        f"\n保存完成: {OUTPUT_FILE}"
    )


if __name__ == "__main__":

    asyncio.run(
        main()
    )
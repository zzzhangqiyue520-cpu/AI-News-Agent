# main.py

import asyncio
import json

from pathlib import Path


from src.ai.analyzer import summarize

from src.sources.deepmind.source import (
    DeepMindSource
)

from src.sources.anthropic.source import (
    AnthropicSource
)

from src.utils import generate_id



# =========================
# 数据目录
# =========================

DATA_DIR = Path("data")


DATA_DIR.mkdir(
    exist_ok=True
)


OUTPUT_FILE = DATA_DIR / "news.json"



# =========================
# 新闻源
# =========================

SOURCES = [

    DeepMindSource(),

    AnthropicSource()

]



# =========================
# 读取历史新闻
# =========================

def load_existing_news():

    if not OUTPUT_FILE.exists():

        return []


    try:

        with open(
            OUTPUT_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)


        if not isinstance(
            data,
            list
        ):

            print(
                "news.json 格式错误。"
            )

            return []


        return data


    except Exception as e:

        print(
            "读取历史新闻失败:",
            e
        )

        return []



# =========================
# 保存新闻
# =========================

def save_news(news_list):

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(

            news_list,

            f,

            ensure_ascii=False,

            indent=4

        )



# =========================
# AI分析
# =========================

def analyze_news(news):

    print(
        "开始 AI 分析:",
        news["title"]
    )


    if not news.get(
        "content"
    ):

        print(
            "没有正文，跳过 AI 分析。"
        )


        return {

            "summary": "",

            "keywords": [],

            "category": "其他"

        }


    try:

        return summarize(
            news
        )


    except Exception as e:

        print(
            "AI 分析失败:",
            e
        )


        return {

            "summary": "",

            "keywords": [],

            "category": "其他"

        }



# =========================
# 主程序
# =========================

async def main():

    print(
        "====== AI News Agent ======"
    )


    # -------------------------
    # 1. 读取历史新闻
    # -------------------------

    existing_news = load_existing_news()


    print(
        f"历史新闻数量: {len(existing_news)}"
    )


    existing_ids = set()


    for news in existing_news:

        if news.get("id"):

            existing_ids.add(
                news["id"]
            )


        elif news.get("url"):

            news_id = generate_id(
                news["url"]
            )


            news["id"] = news_id


            existing_ids.add(
                news_id
            )



    # -------------------------
    # 2. 获取所有新闻源
    # -------------------------

    latest_news = []


    for source in SOURCES:

        try:

            news_list = await source.fetch()


            latest_news.extend(
                news_list
            )


        except Exception as e:

            print(
                f"{source.name} 获取失败:",
                e
            )


    print(
        f"\n本次抓取新闻数量: {len(latest_news)}"
    )



    # -------------------------
    # 3. 去重
    # -------------------------

    new_news = []


    current_ids = set()


    duplicate_count = 0


    for news in latest_news:

        url = news.get(
            "url",
            ""
        ).strip()


        if not url:

            print(
                "新闻缺少 URL，跳过:",
                news.get(
                    "title",
                    ""
                )
            )

            continue


        news_id = generate_id(
            url
        )


        news["id"] = news_id


        # 当前运行批次重复
        if news_id in current_ids:

            duplicate_count += 1

            continue


        current_ids.add(
            news_id
        )


        # 历史新闻重复
        if news_id in existing_ids:

            duplicate_count += 1


            print(
                "重复新闻，跳过:",
                news["title"]
            )


            continue


        new_news.append(
            news
        )



    print(
        f"发现重复新闻: {duplicate_count} 条"
    )


    print(
        f"发现新新闻: {len(new_news)} 条"
    )



    # -------------------------
    # 4. AI分析新新闻
    # -------------------------

    for news in new_news:

        print(
            "\n新新闻:",
            news["title"]
        )


        news["analysis"] = analyze_news(
            news
        )


        existing_news.append(
            news
        )



    # -------------------------
    # 5. 保存
    # -------------------------

    save_news(
        existing_news
    )


    print(
        "\n====== 运行完成 ======"
    )


    print(
        f"历史新闻总数: {len(existing_news)}"
    )


    print(
        f"本次新增: {len(new_news)}"
    )


    print(
        f"本次重复: {duplicate_count}"
    )


    print(
        f"保存位置: {OUTPUT_FILE}"
    )



if __name__ == "__main__":

    asyncio.run(
        main()
    )
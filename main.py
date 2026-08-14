# main.py

import asyncio
import json
from pathlib import Path


# AI
from src.ai.analyzer import summarize


# DeepMind
from src.sources.deepmind.crawler import DeepMindCrawler
from src.sources.deepmind.detail import DeepMindDetail


# Anthropic
from src.sources.anthropic.crawler import fetch_rss
from src.sources.anthropic.parser import parse_rss


# Utils
from src.utils import generate_id



# =========================
# 配置
# =========================

DATA_DIR = Path("data")

DATA_DIR.mkdir(
    exist_ok=True
)


OUTPUT_FILE = DATA_DIR / "news.json"



# =========================
# 读取已有新闻
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


        if not isinstance(data, list):

            print(
                "已有 news.json 格式错误，重新开始。"
            )

            return []


        return data


    except Exception as e:

        print(
            "读取已有新闻失败:",
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
# DeepMind
# =========================

async def get_deepmind_news():

    print(
        "\n开始获取 DeepMind 新闻..."
    )


    crawler = DeepMindCrawler()


    news_list = await crawler.crawl()


    print(
        f"发现 {len(news_list)} 条 DeepMind 新闻"
    )


    detail = DeepMindDetail()


    results = []


    for news in news_list:

        print(
            "正在获取:",
            news["title"]
        )


        try:

            content = await detail.parse_content(
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


        results.append(
            news
        )


    return results



# =========================
# Anthropic
# =========================

async def get_anthropic_news():

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



# =========================
# AI 分析
# =========================

def analyze_news(news):

    print(
        "开始 AI 分析:",
        news["title"]
    )


    if not news.get("content"):

        print(
            "没有正文，跳过 AI 分析。"
        )


        return {

            "summary": "",

            "keywords": [],

            "category": "其他"

        }


    try:

        analysis = summarize(
            news
        )


        return analysis


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


    # 已经存在的新闻 ID
    existing_ids = set()


    # 给历史数据补 ID
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
    # 2. 获取最新新闻
    # -------------------------

    deepmind_news = await get_deepmind_news()


    anthropic_news = await get_anthropic_news()


    latest_news = []


    latest_news.extend(
        deepmind_news
    )


    latest_news.extend(
        anthropic_news
    )


    print(
        f"\n本次抓取新闻数量: {len(latest_news)}"
    )


    # -------------------------
    # 3. 当前批次去重
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
                news.get("title", "")
            )

            continue


        news_id = generate_id(
            url
        )


        news["id"] = news_id


        # 当前批次已经出现过
        if news_id in current_ids:

            duplicate_count += 1

            continue


        current_ids.add(
            news_id
        )


        # 历史数据中已经存在
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
        f"\n发现重复新闻: {duplicate_count} 条"
    )


    print(
        f"发现新新闻: {len(new_news)} 条"
    )


    # -------------------------
    # 4. 只对新新闻调用 AI
    # -------------------------

    for news in new_news:

        print(
            "\n新新闻:",
            news["title"]
        )


        analysis = analyze_news(
            news
        )


        news["analysis"] = analysis


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



# =========================
# 程序入口
# =========================

if __name__ == "__main__":

    asyncio.run(
        main()
    )
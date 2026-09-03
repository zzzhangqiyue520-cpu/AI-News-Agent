# main.py

import asyncio

from src.ai.analyzer import summarize

from src.sources.deepmind.source import (
    DeepMindSource
)

from src.sources.anthropic.source import (
    AnthropicSource
)

from src.utils import generate_id

from src.database import (
    create_table,
    exists_news,
    save_news
)

from src.rag.indexer import (
    build_index
)

from src.logger import logger


# =========================================================
# 新闻源
# =========================================================

SOURCES = [
    DeepMindSource(),
    AnthropicSource()
]


# =========================================================
# AI 新闻分析
# =========================================================

def analyze_news(news):

    logger.info(
        f"开始 AI 分析: {news['title']}"
    )

    # -----------------------------------------------------
    # 没有正文
    # -----------------------------------------------------

    if not news.get("content"):

        logger.warning(
            f"没有正文，跳过 AI 分析: "
            f"{news['title']}"
        )

        return {
            "summary": "",
            "keywords": [],
            "category": "其他"
        }

    # -----------------------------------------------------
    # 调用 LLM
    # -----------------------------------------------------

    try:

        result = summarize(
            news
        )

        logger.info(
            f"AI 分析完成: "
            f"{news['title']}"
        )

        return result

    except Exception as e:

        logger.exception(
            f"AI 分析失败: "
            f"{news['title']} - {e}"
        )

        return {
            "summary": "",
            "keywords": [],
            "category": "其他"
        }


# =========================================================
# 主程序
# =========================================================

async def main():

    logger.info(
        "====== AI News Agent 开始运行 ======"
    )

    try:

        # =================================================
        # 1. 初始化数据库
        # =================================================

        create_table()

        logger.info(
            "数据库初始化完成"
        )


        # =================================================
        # 2. 获取新闻
        # =================================================

        latest_news = []


        for source in SOURCES:

            try:

                logger.info(
                    f"开始获取新闻源: "
                    f"{source.name}"
                )

                news_list = await source.fetch()

                latest_news.extend(
                    news_list
                )

                logger.info(
                    f"{source.name} 获取完成，"
                    f"共 {len(news_list)} 条"
                )

            except Exception as e:

                logger.exception(
                    f"{source.name} 获取失败: "
                    f"{e}"
                )


        logger.info(
            f"本次总抓取新闻数量: "
            f"{len(latest_news)}"
        )


        # =================================================
        # 3. 新闻去重
        # =================================================

        new_count = 0

        duplicate_count = 0

        current_ids = set()


        for news in latest_news:

            # -------------------------------------------------
            # 检查 URL
            # -------------------------------------------------

            url = news.get(
                "url",
                ""
            ).strip()


            if not url:

                logger.warning(
                    f"新闻缺少 URL，跳过: "
                    f"{news.get('title', '')}"
                )

                continue


            # -------------------------------------------------
            # 根据 URL 生成唯一 ID
            # -------------------------------------------------

            news_id = generate_id(
                url
            )

            news["id"] = news_id


            # -------------------------------------------------
            # 当前批次重复
            # -------------------------------------------------

            if news_id in current_ids:

                duplicate_count += 1

                logger.info(
                    f"当前批次重复，跳过: "
                    f"{news['title']}"
                )

                continue


            current_ids.add(
                news_id
            )


            # -------------------------------------------------
            # 数据库历史重复
            # -------------------------------------------------

            if exists_news(
                news_id
            ):

                duplicate_count += 1

                logger.info(
                    f"历史新闻，跳过: "
                    f"{news['title']}"
                )

                continue


            # =================================================
            # 4. AI 分析
            # =================================================

            news["analysis"] = analyze_news(
                news
            )


            # =================================================
            # 5. 保存 SQLite
            # =================================================

            try:

                save_result = save_news(
                    news
                )


                # -------------------------------------------------
                # save_news() 返回 False
                # -------------------------------------------------

                if save_result is False:

                    logger.error(
                        f"新闻保存失败: "
                        f"{news['title']}"
                    )

                    continue


                new_count += 1

                logger.info(
                    f"保存新闻成功: "
                    f"{news['title']}"
                )

            except Exception as e:

                logger.exception(
                    f"新闻保存失败: "
                    f"{news['title']} - {e}"
                )


        # =================================================
        # 6. 增量更新 Chroma
        #
        # 注意：
        # 必须放在 for 循环之后。
        #
        # 这样所有新闻保存完成后，
        # 只调用一次 build_index()。
        # =================================================

        try:

            logger.info(
                "开始更新 Chroma 增量索引"
            )

            build_index()

            logger.info(
                "Chroma 增量索引更新完成"
            )

        except Exception as e:

            logger.exception(
                f"Chroma 增量索引失败: "
                f"{e}"
            )


        # =================================================
        # 7. 运行统计
        # =================================================

        logger.info(
            "====== 本次运行完成 ======"
        )

        logger.info(
            f"新增: {new_count}"
        )

        logger.info(
            f"重复: {duplicate_count}"
        )

        logger.info(
            f"本次抓取: {len(latest_news)}"
        )

        logger.info(
            "====== AI News Agent 结束运行 ======"
        )


    # =====================================================
    # 8. 主程序级异常
    # =====================================================

    except Exception as e:

        logger.exception(
            f"主程序发生未处理异常: "
            f"{e}"
        )

        raise


# =========================================================
# 程序入口
# =========================================================

if __name__ == "__main__":

    asyncio.run(
        main()
    )
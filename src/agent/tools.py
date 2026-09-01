# src/agent/tools.py

from src.database import (
    get_latest_news,
    get_news_by_category,
    get_news_by_source,
    search_news,
    get_news_detail
)

from src.rag.retriever import (
    retrieve_news
)


# =========================================================
# 最新新闻
# =========================================================

def search_latest_news(limit=5):

    rows = get_latest_news(
        limit
    )

    results = []

    for item in rows:

        results.append({
            "id": item[0],
            "title": item[1],
            "url": item[2],
            "source": item[3],
            "summary": item[4],
            "category": item[5]
        })

    return results


# =========================================================
# 分类搜索
# =========================================================

def search_category_news(category):

    rows = get_news_by_category(
        category
    )

    results = []

    for item in rows:

        results.append({
            "id": item[0],
            "title": item[1],
            "url": item[2],
            "source": item[3],
            "summary": item[4],
            "category": item[5]
        })

    return results


# =========================================================
# 来源搜索
# =========================================================

def search_source_news(source):

    rows = get_news_by_source(
        source
    )

    results = []

    for item in rows:

        results.append({
            "id": item[0],
            "title": item[1],
            "url": item[2],
            "source": item[3],
            "summary": item[4],
            "category": item[5]
        })

    return results


# =========================================================
# 关键词搜索
# =========================================================

def search_keyword(keyword):

    rows = search_news(
        keyword
    )

    results = []

    for item in rows:

        results.append({
            "id": item[0],
            "title": item[1],
            "url": item[2],
            "source": item[3],
            "summary": item[4],
            "category": item[5]
        })

    return results


# =========================================================
# 新闻详情
# =========================================================

def get_news_detail_tool(news_id):

    """
    根据新闻ID读取完整新闻正文。

    这个工具用于：
    先通过搜索工具找到新闻，
    再根据ID读取完整content。
    """

    row = get_news_detail(
        news_id
    )

    if not row:

        return {
            "error": "没有找到对应新闻"
        }

    return {
        "id": row[0],
        "title": row[2],
        "url": row[3],
        "source": row[4],
        "content": row[5],
        "summary": row[6],
        "category": row[7]
    }

def search_knowledge(
    query,
    limit=5,
    category=None,
    source=None
):

    results = retrieve_news(

        query=query,

        limit=limit,

        category=category,

        source=source

    )

    return results


# =========================================================
# 统一工具执行器
# =========================================================

def execute_tool(
    tool_name,
    arguments
):

    if tool_name == "search_latest_news":

        limit = arguments.get(
            "limit",
            5
        )

        if not isinstance(
            limit,
            int
        ):
            limit = 5

        limit = max(
            1,
            min(
                limit,
                10
            )
        )

        return search_latest_news(
            limit
        )


    elif tool_name == "search_category_news":

        category = arguments.get(
            "category",
            ""
        )

        if not category:

            return []

        return search_category_news(
            category
        )


    elif tool_name == "search_source_news":

        source = arguments.get(
            "source",
            ""
        )

        if not source:

            return []

        return search_source_news(
            source
        )


    elif tool_name == "search_keyword":

        keyword = arguments.get(
            "keyword",
            ""
        )

        if not keyword:

            return []

        return search_keyword(
            keyword
        )


    elif tool_name == "get_news_detail":

        news_id = arguments.get(
            "news_id"
        )

        if news_id is None:

            return {
                "error": "缺少 news_id"
            }

        return get_news_detail_tool(
            news_id
        )



    elif tool_name == "search_knowledge":

        query = arguments.get(

            "query",

            ""

        )

        limit = arguments.get(

            "limit",

            5

        )

        category = arguments.get(

            "category"

        )

        source = arguments.get(

            "source"

        )

        if not query:
            return []

        if not isinstance(

                limit,

                int

        ):
            limit = 5

        limit = max(

            1,

            min(

                limit,

                5

            )

        )

        return search_knowledge(

            query=query,

            limit=limit,

            category=category,

            source=source

        )

    else:

        raise ValueError(
            f"未知工具: {tool_name}"
        )
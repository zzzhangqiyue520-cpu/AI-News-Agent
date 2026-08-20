from src.database import (
    get_latest_news,
    get_news_by_category,
    search_news
)



# =========================
# 最新新闻
# =========================

def search_latest_news(limit=5):


    rows = get_latest_news(
        limit
    )


    results=[]


    for item in rows:


        results.append({

            "title": item[1],

            "source": item[3],

            "category": item[5],

            "summary": item[4]

        })


    return results





# =========================
# 分类查询
# =========================

def search_category_news(category):


    rows = get_news_by_category(
        category
    )


    results=[]


    for item in rows:


        results.append({

            "title": item[1],

            "source": item[3],

            "category": item[5],

            "summary": item[4]

        })


    return results





# =========================
# 关键词搜索
# =========================

def search_keyword(keyword):


    rows = search_news(
        keyword
    )


    results=[]


    for item in rows:


        results.append({

            "title": item[1],

            "source": item[3],

            "category": item[5],

            "summary": item[4]

        })


    return results
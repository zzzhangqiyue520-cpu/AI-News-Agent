import sqlite3
import time
from pathlib import Path


DB_PATH = Path(
    "data/news.db"
)


# ======================
# 获取数据库连接
# ======================

def get_connection():

    DB_PATH.parent.mkdir(
        exist_ok=True
    )

    conn = sqlite3.connect(
        DB_PATH
    )

    return conn


# ======================
# 创建数据库
# ======================

def create_table():

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS news(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            hash TEXT UNIQUE,

            title TEXT,

            url TEXT UNIQUE,

            source TEXT,

            content TEXT,

            summary TEXT,

            category TEXT,

            created_at INTEGER

        )
        """
    )


    # 来源索引
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_source
        ON news(source)
        """
    )


    # 分类索引
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_category
        ON news(category)
        """
    )


    # 时间索引
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_time
        ON news(created_at)
        """
    )


    conn.commit()

    conn.close()


# ======================
# 判断新闻是否存在
# ======================

def exists_news(news_hash):

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT id
        FROM news
        WHERE hash = ?
        """,
        (
            news_hash,
        )
    )


    result = cursor.fetchone()


    conn.close()


    return result is not None


# ======================
# 保存新闻
# ======================

def save_news(news):

    conn = get_connection()

    cursor = conn.cursor()


    analysis = news.get(
        "analysis",
        {}
    )


    cursor.execute(
        """
        INSERT OR IGNORE INTO news(

            hash,

            title,

            url,

            source,

            content,

            summary,

            category,

            created_at

        )

        VALUES(?,?,?,?,?,?,?,?)
        """,
        (
            news["id"],

            news["title"],

            news["url"],

            news.get(
                "source",
                ""
            ),

            news.get(
                "content",
                ""
            ),

            analysis.get(
                "summary",
                ""
            ),

            analysis.get(
                "category",
                "其他"
            ),

            int(
                time.time()
            )
        )
    )


    conn.commit()

    conn.close()


# ======================
# 查询最新新闻
# ======================

def get_latest_news(
        limit=10
):

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT

            id,

            title,

            url,

            source,

            summary,

            category,

            created_at

        FROM news

        ORDER BY created_at DESC

        LIMIT ?
        """,
        (
            limit,
        )
    )


    rows = cursor.fetchall()


    conn.close()


    return rows


# ======================
# 根据来源查询新闻
# ======================

def get_news_by_source(
        source,
        limit=20
):

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT

            id,

            title,

            url,

            source,

            summary,

            category,

            created_at

        FROM news

        WHERE source = ?

        ORDER BY created_at DESC

        LIMIT ?
        """,
        (
            source,
            limit
        )
    )


    rows = cursor.fetchall()


    conn.close()


    return rows


# ======================
# 根据分类查询新闻
# ======================

def get_news_by_category(
        category,
        limit=20
):

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT

            id,

            title,

            url,

            source,

            summary,

            category,

            created_at

        FROM news

        WHERE category = ?

        ORDER BY created_at DESC

        LIMIT ?
        """,
        (
            category,
            limit
        )
    )


    rows = cursor.fetchall()


    conn.close()


    return rows


# ======================
# 关键词搜索
# ======================

def search_news(
        keyword,
        limit=20
):

    keyword = keyword.strip()


    if not keyword:

        return []


    conn = get_connection()

    cursor = conn.cursor()


    pattern = f"%{keyword}%"


    cursor.execute(
        """
        SELECT

            id,

            title,

            url,

            source,

            summary,

            category,

            created_at

        FROM news

        WHERE

            title LIKE ?

            OR summary LIKE ?

            OR category LIKE ?

        ORDER BY created_at DESC

        LIMIT ?
        """,
        (
            pattern,

            pattern,

            pattern,

            limit
        )
    )


    rows = cursor.fetchall()


    conn.close()


    return rows


# ======================
# 查询新闻详情
# ======================

def get_news_detail(
        news_id
):

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT

            id,

            hash,

            title,

            url,

            source,

            content,

            summary,

            category,

            created_at

        FROM news

        WHERE id = ?
        """,
        (
            news_id,
        )
    )


    row = cursor.fetchone()


    conn.close()


    return row


# ======================
# 新闻总数
# ======================

def count_news():

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT COUNT(*)
        FROM news
        """
    )


    count = cursor.fetchone()[0]


    conn.close()


    return count
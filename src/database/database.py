import sqlite3
import time
from pathlib import Path



DB_PATH = Path(
    "data/news.db"
)



def get_connection():

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


    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_source
        ON news(source)
        """
    )


    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_category
        ON news(category)
        """
    )


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
        WHERE hash=?

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


    sql = """

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

    """



    cursor.execute(

        sql,

        (

            news["id"],

            news["title"],

            news["url"],

            news["source"],

            news["content"],

            news["analysis"]["summary"],

            news["analysis"]["category"],

            int(time.time())

        )

    )


    conn.commit()

    conn.close()





# ======================
# 查询新闻
# ======================

def get_latest_news(limit=10):


    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(

        """

        SELECT

        title,

        source,

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
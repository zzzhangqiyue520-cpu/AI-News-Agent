# src/rag/indexer.py

import chromadb

from sentence_transformers import SentenceTransformer

from src.database import (
    PROJECT_ROOT,
    get_news
)

from src.rag.chunker import (
    split_text
)


# =========================================================
# 配置
# =========================================================

CHROMA_DIR = (
    PROJECT_ROOT
    / "data"
    / "chroma"
)

COLLECTION_NAME = "news"

MODEL_NAME = (
    "paraphrase-multilingual-MiniLM-L12-v2"
)


# =========================================================
# 获取 Embedding 模型
# =========================================================

def get_embedding_model():

    print(
        "正在加载本地 Embedding 模型..."
    )

    model = SentenceTransformer(
        MODEL_NAME,
        local_files_only=True
    )

    print(
        "Embedding 模型加载完成。"
    )

    return model


# =========================================================
# 获取 Chroma Collection
# =========================================================

def get_collection():

    client = chromadb.PersistentClient(
        path=str(
            CHROMA_DIR
        )
    )

    collection = (
        client.get_or_create_collection(
            name=COLLECTION_NAME
        )
    )

    return collection


# =========================================================
# 获取已经存在的新闻 ID
# =========================================================

def get_indexed_news_ids(
    collection
):

    """
    获取已经进入 Chroma 的新闻 ID。

    Chroma 中一篇新闻可能对应多个 Chunk。
    只要某个 news_id 已经出现，
    就认为这篇新闻已经完成索引。
    """

    if collection.count() == 0:

        return set()

    result = collection.get(
        include=[
            "metadatas"
        ]
    )

    metadatas = result.get(
        "metadatas",
        []
    )

    indexed_ids = set()

    for metadata in metadatas:

        if not metadata:
            continue

        news_id = metadata.get(
            "news_id"
        )

        if news_id is None:
            continue

        indexed_ids.add(
            str(news_id)
        )

    return indexed_ids


# =========================================================
# 主索引函数
# =========================================================

def build_index():

    print(
        "\n====== 开始增量构建新闻向量库 ======"
    )

    # -----------------------------------------------------
    # 显示路径
    # -----------------------------------------------------

    print(
        f"SQLite 数据库: "
        f"{PROJECT_ROOT / 'data' / 'news.db'}"
    )

    print(
        f"Chroma 数据位置: "
        f"{CHROMA_DIR}"
    )

    # -----------------------------------------------------
    # 获取数据库新闻
    # -----------------------------------------------------

    rows = get_news()

    print(
        f"SQLite 新闻数量: {len(rows)}"
    )

    # -----------------------------------------------------
    # 获取 Chroma
    # -----------------------------------------------------

    collection = get_collection()

    chroma_count = collection.count()

    print(
        f"Chroma 当前数量: "
        f"{chroma_count}"
    )

    # -----------------------------------------------------
    # 获取已经索引的新闻 ID
    # -----------------------------------------------------

    indexed_news_ids = (
        get_indexed_news_ids(
            collection
        )
    )

    print(
        f"Chroma 已存在新闻数量: "
        f"{len(indexed_news_ids)}"
    )

    # -----------------------------------------------------
    # 找出新增新闻
    # -----------------------------------------------------

    new_rows = []

    for row in rows:

        news_id = str(
            row[0]
        )

        if news_id not in indexed_news_ids:

            new_rows.append(
                row
            )

    # -----------------------------------------------------
    # 没有新增新闻
    # -----------------------------------------------------

    if not new_rows:

        print(
            "没有发现新的新闻。"
        )

        print(
            "无需进行 Embedding。"
        )

        print(
            "====== 增量索引完成 ======\n"
        )

        return

    print(
        f"发现新增新闻: "
        f"{len(new_rows)} 条"
    )

    # -----------------------------------------------------
    # 加载 Embedding 模型
    #
    # 只有发现新增新闻时才加载
    # -----------------------------------------------------

    model = get_embedding_model()

    documents = []

    metadatas = []

    ids = []

    # -----------------------------------------------------
    # 处理新增新闻
    # -----------------------------------------------------

    for row in new_rows:

        news_id = str(
            row[0]
        )

        title = row[2]

        url = row[3]

        source = row[4]

        content = row[5] or ""

        summary = row[6] or ""

        category = row[7] or ""

        # -------------------------------------------------
        # 正文为空时使用摘要
        # -------------------------------------------------

        if not content:

            content = summary or ""

        # -------------------------------------------------
        # 没有任何文本
        # -------------------------------------------------

        if not content:

            print(
                f"新闻 {news_id} "
                f"没有可用文本，跳过。"
            )

            continue

        # -------------------------------------------------
        # Chunk
        # -------------------------------------------------

        chunks = split_text(
            content
        )

        print(
            f"新闻 {news_id}: "
            f"{len(chunks)} 个 Chunk"
        )

        # -------------------------------------------------
        # 保存 Chunk
        # -------------------------------------------------

        for chunk_index, chunk in enumerate(
            chunks
        ):

            chunk_id = (
                f"{news_id}_{chunk_index}"
            )

            ids.append(
                chunk_id
            )

            documents.append(
                chunk
            )

            metadatas.append({

                "news_id":
                    news_id,

                "title":
                    title or "",

                "url":
                    url or "",

                "source":
                    source or "",

                "category":
                    category or "",

                "chunk_index":
                    chunk_index

            })

    # -----------------------------------------------------
    # 没有可用 Chunk
    # -----------------------------------------------------

    if not documents:

        print(
            "没有找到可以进行 Embedding 的新文本。"
        )

        print(
            "====== 增量索引结束 ======\n"
        )

        return

    print(
        f"准备向量化 "
        f"{len(documents)} 个新 Chunk..."
    )

    # -----------------------------------------------------
    # Embedding
    # -----------------------------------------------------

    embeddings = model.encode(
        documents,
        normalize_embeddings=True,
        show_progress_bar=True
    ).tolist()

    print(
        "Embedding 生成完成。"
    )

    # -----------------------------------------------------
    # 写入 Chroma
    # -----------------------------------------------------

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings
    )

    # -----------------------------------------------------
    # 最终统计
    # -----------------------------------------------------

    final_count = collection.count()

    print(
        "\n====== 向量库增量更新完成 ======"
    )

    print(
        f"新增新闻数量: "
        f"{len(new_rows)}"
    )

    print(
        f"新增 Chunk 数量: "
        f"{len(documents)}"
    )

    print(
        f"Chroma 当前 Chunk 数量: "
        f"{final_count}"
    )

    print(
        "================================\n"
    )


# =========================================================
# 程序入口
# =========================================================

if __name__ == "__main__":

    build_index()
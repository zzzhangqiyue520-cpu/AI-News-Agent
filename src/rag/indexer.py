# src/rag/indexer.py


import chromadb


from sentence_transformers import (
    SentenceTransformer
)


from src.database import (
    PROJECT_ROOT,
    DB_PATH,
    create_table,
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
        "正在加载 Embedding 模型..."
    )


    model = SentenceTransformer(
        MODEL_NAME
    )


    print(
        "Embedding 模型加载完成。"
    )


    return model


# =========================================================
# 获取 Chroma
# =========================================================

def get_collection():

    CHROMA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


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
# 构建向量库
# =========================================================

def build_index():

    print(
        "====== 开始构建 Chunk 向量库 ======"
    )


    print(
        "SQLite 数据库:",
        DB_PATH
    )


    # -----------------------------------------------------
    # 确保数据库表存在
    # -----------------------------------------------------

    create_table()


    # -----------------------------------------------------
    # 读取新闻
    # -----------------------------------------------------

    rows = get_news()


    print(
        f"SQLite 新闻数量: {len(rows)}"
    )


    if not rows:

        print(
            "没有新闻。"
        )

        return


    # -----------------------------------------------------
    # Embedding 模型
    # -----------------------------------------------------

    model = get_embedding_model()


    # -----------------------------------------------------
    # Chroma
    # -----------------------------------------------------

    collection = get_collection()


    # -----------------------------------------------------
    # 清空旧 Collection
    # -----------------------------------------------------

    print(
        "清理旧向量数据..."
    )


    old_ids = collection.get().get(
        "ids",
        []
    )


    if old_ids:

        collection.delete(
            ids=old_ids
        )


    documents = []

    ids = []

    metadatas = []


    total_chunks = 0


    # -----------------------------------------------------
    # 新闻 → Chunk
    # -----------------------------------------------------

    for row in rows:

        news_id = row[0]

        title = row[2]

        url = row[3]

        source = row[4]

        content = row[5]

        category = row[7]


        if not content:

            print(
                f"跳过无正文新闻: {title}"
            )

            continue


        # ---------------------------------------------
        # 切分
        # ---------------------------------------------

        chunks = split_text(

            content,

            chunk_size=1000,

            overlap=200

        )


        print(
            f"{title} -> {len(chunks)} 个 Chunk"
        )


        # ---------------------------------------------
        # 每个 Chunk 独立进入向量库
        # ---------------------------------------------

        for chunk_index, chunk in enumerate(
            chunks
        ):

            chunk_id = (
                f"{news_id}_{chunk_index}"
            )


            document = (
                f"标题：{title}\n"
                f"来源：{source}\n"
                f"分类：{category}\n\n"
                f"{chunk}"
            )


            documents.append(
                document
            )


            ids.append(
                chunk_id
            )


            metadatas.append(
                {
                    "news_id": news_id,

                    "title": title,

                    "url": url,

                    "source": source,

                    "category": category,

                    "chunk_index":
                        chunk_index
                }
            )


            total_chunks += 1


    if not documents:

        print(
            "没有可建立向量的 Chunk。"
        )

        return


    print(
        f"\n总 Chunk 数量: {total_chunks}"
    )


    # -----------------------------------------------------
    # Embedding
    # -----------------------------------------------------

    print(
        "开始生成 Embedding..."
    )


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

    collection.upsert(

        ids=ids,

        documents=documents,

        embeddings=embeddings,

        metadatas=metadatas

    )


    print(
        "\n====== Chunk 向量库构建完成 ======"
    )


    print(
        f"新闻数量: {len(rows)}"
    )


    print(
        f"Chunk 数量: {total_chunks}"
    )


    print(
        "Chroma 数据位置:",
        CHROMA_DIR
    )


    print(
        "Chroma 当前数量:",
        collection.count()
    )


if __name__ == "__main__":

    build_index()
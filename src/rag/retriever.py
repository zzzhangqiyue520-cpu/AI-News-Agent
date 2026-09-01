# src/rag/retriever.py

import re

import chromadb

from sentence_transformers import (
    SentenceTransformer
)

from src.database import (
    PROJECT_ROOT,
    search_news
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
# Embedding 模型
# =========================================================

_model = None


def get_embedding_model():

    global _model


    if _model is None:

        print(
            "正在加载本地 Embedding 模型..."
        )


        try:

            _model = SentenceTransformer(

                MODEL_NAME,

                local_files_only=True

            )


        except Exception as e:

            print(
                "本地 Embedding 模型加载失败:"
            )

            print(
                e
            )

            raise


        print(
            "Embedding 模型加载完成。"
        )


    return _model


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
# 提取简单关键词
# =========================================================

def extract_keywords(query):

    query = query.strip()


    if not query:

        return []


    stop_words = {

        "最近",
        "现在",
        "当前",
        "有哪些",
        "有什么",
        "哪些",
        "什么",
        "新闻",
        "消息",
        "相关",
        "方面",
        "情况",
        "一下",
        "具体",
        "讲了什么",
        "是什么",
        "怎么样",
        "如何",
        "为什么",
        "比较",
        "介绍",
        "介绍一下",
        "主要",
        "进展",
        "的话",
        "的",
        "了",
        "呢",
        "吗",
        "和",
        "与",
        "及",
        "在",
        "是",
        "有",
        "？",
        "?",
        "。",
        ".",
        "！",
        "!",
        "，",
        ","

    }


    # -----------------------------------------------------
    # 英文 / 数字实体
    # -----------------------------------------------------

    english_words = re.findall(

        r"[A-Za-z][A-Za-z0-9.-]*",

        query

    )


    # -----------------------------------------------------
    # 中文 AI 关键词
    # -----------------------------------------------------

    chinese_candidates = [

        "人工智能",
        "AI",

        "机器人",
        "具身智能",
        "具身机器人",

        "大模型",
        "模型",

        "开源",
        "开源模型",

        "科研",
        "研究",

        "多智能体",
        "智能体",
        "Agent",

        "安全",
        "AI安全",
        "网络安全",

        "语音",
        "翻译",

        "视觉",
        "多模态",

        "训练",
        "推理",

        "芯片",

        "企业",

        "教育",

        "医疗"

    ]


    chinese_keywords = []


    for word in chinese_candidates:

        if word in query:

            chinese_keywords.append(
                word
            )


    raw_keywords = (
        english_words
        + chinese_keywords
    )


    keywords = []


    for keyword in raw_keywords:

        keyword = keyword.strip()


        if not keyword:

            continue


        if keyword in stop_words:

            continue


        if keyword not in keywords:

            keywords.append(
                keyword
            )


    return keywords


# =========================================================
# Vector Retrieval
# =========================================================

def retrieve_vector(
    query,
    limit=10
):

    query = query.strip()


    if not query:

        return []


    collection = get_collection()


    count = collection.count()


    if count == 0:

        return []


    limit = min(
        limit,
        count
    )


    # -----------------------------------------------------
    # 获取 Embedding 模型
    # -----------------------------------------------------

    model = get_embedding_model()


    # -----------------------------------------------------
    # Query → Embedding
    # -----------------------------------------------------

    query_embedding = (

        model.encode(

            [query],

            normalize_embeddings=True

        )

        .tolist()

    )


    # -----------------------------------------------------
    # Chroma 搜索
    # -----------------------------------------------------

    results = collection.query(

        query_embeddings=query_embedding,

        n_results=limit

    )


    documents = results.get(
        "documents",
        [[]]
    )[0]


    metadatas = results.get(
        "metadatas",
        [[]]
    )[0]


    distances = results.get(
        "distances",
        [[]]
    )[0]


    news_list = []


    for document, metadata, distance in zip(

        documents,

        metadatas,

        distances

    ):

        news_id = metadata.get(
            "news_id"
        )


        if news_id is None:

            continue


        # -------------------------------------------------
        # 距离 → score
        # -------------------------------------------------

        vector_score = (

            1
            /
            (1 + distance)

        )


        news_list.append({

            "id":
                news_id,

            "title":
                metadata.get(
                    "title",
                    ""
                ),

            "url":
                metadata.get(
                    "url",
                    ""
                ),

            "source":
                metadata.get(
                    "source",
                    ""
                ),

            "category":
                metadata.get(
                    "category",
                    ""
                ),

            "content":
                document,

            "distance":
                distance,

            "vector_score":
                vector_score,

            "keyword_score":
                0.0,

            "matched_keywords":
                []

        })


    return news_list


# =========================================================
# Keyword Retrieval
# =========================================================

def retrieve_keyword(
    query,
    limit=10
):

    keywords = extract_keywords(
        query
    )


    if not keywords:

        return []


    print(
        f"关键词检索: {keywords}"
    )


    all_results = []


    # -----------------------------------------------------
    # 每个关键词搜索
    # -----------------------------------------------------

    for keyword in keywords:

        rows = search_news(

            keyword,

            limit

        )


        for item in rows:

            all_results.append({

                "id":
                    item[0],

                "title":
                    item[1],

                "url":
                    item[2],

                "source":
                    item[3],

                "summary":
                    item[4],

                "category":
                    item[5],

                "content":
                    "",

                "distance":
                    None,

                "vector_score":
                    0.0,

                "keyword_score":
                    1.0,

                "matched_keywords":
                    [keyword]

            })


    if not all_results:

        return []


    # -----------------------------------------------------
    # 新闻去重
    # -----------------------------------------------------

    unique_results = {}


    for item in all_results:

        news_id = item["id"]


        if news_id not in unique_results:

            unique_results[
                news_id
            ] = item

            continue


        old_keywords = (

            unique_results[
                news_id
            ][
                "matched_keywords"
            ]

        )


        for keyword in item[
            "matched_keywords"
        ]:

            if keyword not in old_keywords:

                old_keywords.append(
                    keyword
                )


    return list(
        unique_results.values()
    )[:limit]


# =========================================================
# Hybrid Retrieval
# =========================================================

def retrieve_news(
    query,
    limit=5
):

    query = query.strip()


    if not query:

        return []


    # -----------------------------------------------------
    # Vector Retrieval
    # -----------------------------------------------------

    vector_results = retrieve_vector(

        query,

        limit=max(
            limit * 5,
            10
        )

    )


    # -----------------------------------------------------
    # Keyword Retrieval
    # -----------------------------------------------------

    keyword_results = retrieve_keyword(

        query,

        limit=max(
            limit * 5,
            10
        )

    )


    # -----------------------------------------------------
    # 合并结果
    # -----------------------------------------------------

    merged = {}


    # Vector

    for item in vector_results:

        news_id = item["id"]


        if news_id not in merged:

            merged[news_id] = item


    # Keyword

    for item in keyword_results:

        news_id = item["id"]


        if news_id not in merged:

            merged[news_id] = item

        else:

            merged[
                news_id
            ]["keyword_score"] = (

                item[
                    "keyword_score"
                ]

            )


            old_keywords = (
                merged[
                    news_id
                ].get(
                    "matched_keywords",
                    []
                )
            )


            for keyword in item[
                "matched_keywords"
            ]:

                if keyword not in old_keywords:

                    old_keywords.append(
                        keyword
                    )


    # -----------------------------------------------------
    # Hybrid Score
    # -----------------------------------------------------

    for item in merged.values():

        vector_score = item.get(
            "vector_score",
            0.0
        )


        keyword_score = item.get(
            "keyword_score",
            0.0
        )


        item["hybrid_score"] = (

            0.7 * vector_score

            +

            0.3 * keyword_score

        )


    # -----------------------------------------------------
    # 排序
    # -----------------------------------------------------

    results = list(
        merged.values()
    )


    results.sort(

        key=lambda item:
            item["hybrid_score"],

        reverse=True

    )


    return results[:limit]
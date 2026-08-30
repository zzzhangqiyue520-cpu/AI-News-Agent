# src/rag/retriever.py

import re
from pathlib import Path

import chromadb

from sentence_transformers import SentenceTransformer

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

model = SentenceTransformer(
    MODEL_NAME
)


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
    """
    从用户问题中提取用于 SQLite 关键词搜索的关键词。

    当前采用简单规则：
    1. 提取英文 / 数字实体
    2. 提取常见中文 AI 新闻关键词
    3. 去除常见停用词
    """

    query = query.strip()

    if not query:
        return []


    # -----------------------------------------------------
    # 常见停用词
    # -----------------------------------------------------

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
        "什么",
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
    #
    # Gemini
    # Gemini 3.5
    # Claude
    # Robotics
    # AI
    # -----------------------------------------------------

    english_words = re.findall(
        r"[A-Za-z][A-Za-z0-9.-]*",
        query
    )


    # -----------------------------------------------------
    # 常见中文关键词
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


    # -----------------------------------------------------
    # 合并
    # -----------------------------------------------------

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


        if len(keyword) == 1 and not re.match(
            r"[A-Za-z0-9]",
            keyword
        ):
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


    collection_count = (
        collection.count()
    )


    if collection_count == 0:

        return []


    limit = min(
        limit,
        collection_count
    )


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


        # cosine distance
        #
        # 距离越小越相关
        #
        # 转成一个简单的 0~1 左右的 score

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
    # 每一个关键词分别搜索
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
    # 同一新闻去重
    #
    # 同一篇新闻可能命中多个关键词
    # -----------------------------------------------------

    unique_results = {}


    for item in all_results:

        news_id = item["id"]


        if news_id not in unique_results:

            unique_results[news_id] = item

            continue


        # 已存在：
        # 合并关键词

        old_keywords = unique_results[
            news_id
        ]["matched_keywords"]


        for keyword in item[
            "matched_keywords"
        ]:

            if keyword not in old_keywords:

                old_keywords.append(
                    keyword
                )


        # 当前版本：
        # 命中关键词就算 keyword_score = 1

        unique_results[
            news_id
        ]["keyword_score"] = 1.0


    results = list(
        unique_results.values()
    )


    return results[:limit]


# =========================================================
# Hybrid Retrieval
# =========================================================

def retrieve_news(
    query,
    limit=5
):

    """
    混合检索。

    同时执行：

    1. Vector Retrieval
    2. Keyword Retrieval

    然后：

    合并
    ↓
    按 news_id 去重
    ↓
    计算综合分数
    ↓
    排序
    ↓
    返回 Top-K
    """

    query = query.strip()


    if not query:

        return []


    # -----------------------------------------------------
    # 1. Vector Retrieval
    #
    # 多取一些候选，方便后面去重/合并
    # -----------------------------------------------------

    vector_results = retrieve_vector(

        query,

        limit=max(
            limit * 5,
            10
        )

    )


    # -----------------------------------------------------
    # 2. Keyword Retrieval
    # -----------------------------------------------------

    keyword_results = retrieve_keyword(

        query,

        limit=max(
            limit * 5,
            10
        )

    )


    # -----------------------------------------------------
    # 3. 合并
    # -----------------------------------------------------

    merged = {}


    # 先加入向量结果

    for item in vector_results:

        news_id = item["id"]


        if news_id not in merged:

            merged[news_id] = item


    # 再加入关键词结果

    for item in keyword_results:

        news_id = item["id"]


        if news_id not in merged:

            merged[news_id] = item

        else:

            # 保存关键词命中状态

            merged[
                news_id
            ]["keyword_score"] = (

                item[
                    "keyword_score"
                ]

            )


            # 合并匹配关键词

            old_keywords = merged[
                news_id
            ].get(
                "matched_keywords",
                []
            )


            for keyword in item[
                "matched_keywords"
            ]:

                if keyword not in old_keywords:

                    old_keywords.append(
                        keyword
                    )


    # -----------------------------------------------------
    # 4. 计算 Hybrid Score
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


        # -------------------------------------------------
        # 当前版本：
        #
        # Vector 70%
        # Keyword 30%
        # -------------------------------------------------

        item["hybrid_score"] = (

            0.7 * vector_score

            +

            0.3 * keyword_score

        )


    # -----------------------------------------------------
    # 5. 排序
    # -----------------------------------------------------

    results = list(
        merged.values()
    )


    results.sort(

        key=lambda item:
            item["hybrid_score"],

        reverse=True

    )


    # -----------------------------------------------------
    # 6. 返回 Top-K
    # -----------------------------------------------------

    return results[:limit]
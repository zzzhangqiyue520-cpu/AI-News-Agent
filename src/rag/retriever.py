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
# 提取关键词
# =========================================================

def extract_keywords(query):

    query = query.strip()


    if not query:

        return []


    # -----------------------------------------------------
    # 停用词
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
    # 例如：
    #
    # Gemini
    # Robotics
    # GPT-5
    # Claude
    # -----------------------------------------------------

    english_words = re.findall(

        r"[A-Za-z][A-Za-z0-9.-]*",

        query

    )


    # -----------------------------------------------------
    # 中文关键词
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
    # 合并关键词
    # -----------------------------------------------------

    raw_keywords = (

        english_words

        +

        chinese_keywords

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

    limit=10,

    category=None,

    source=None

):

    query = query.strip()


    if not query:

        return []


    collection = get_collection()


    count = collection.count()


    if count == 0:

        return []


    # -----------------------------------------------------
    # 先获取 Embedding 模型
    # -----------------------------------------------------

    model = get_embedding_model()


    # -----------------------------------------------------
    # query → embedding
    # -----------------------------------------------------

    query_embedding = (

        model.encode(

            [query],

            normalize_embeddings=True

        )

        .tolist()

    )


    # -----------------------------------------------------
    # 构建 Chroma 查询参数
    # -----------------------------------------------------

    query_kwargs = {

        "query_embeddings":
            query_embedding,

        "n_results":
            min(
                limit,
                count
            )

    }

    # =====================================================
    # Metadata Filter
    # =====================================================

    where_conditions = []

    # -----------------------------------------------------
    # 分类过滤
    # -----------------------------------------------------

    if category:
        where_conditions.append(
            {
                "category": {
                    "$eq": category
                }
            }
        )

    # -----------------------------------------------------
    # 来源过滤
    # -----------------------------------------------------

    if source:
        where_conditions.append(
            {
                "source": {
                    "$eq": source
                }
            }
        )

    # -----------------------------------------------------
    # 根据条件数量构建 where
    # -----------------------------------------------------

    if len(where_conditions) == 1:

        where = where_conditions[0]


    elif len(where_conditions) > 1:

        where = {
            "$and": where_conditions
        }


    else:

        where = None

    # -----------------------------------------------------
    # 加入 Chroma 查询参数
    # -----------------------------------------------------

    if where is not None:
        query_kwargs["where"] = where

        print(
            f"RAG Metadata Filter: {where}"
        )


    # -----------------------------------------------------
    # Chroma 查询
    # -----------------------------------------------------

    results = collection.query(

        **query_kwargs

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


    for (

        document,

        metadata,

        distance

    ) in zip(

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
        # distance → vector score
        # -------------------------------------------------

        vector_score = (

            1.0
            /
            (
                1.0
                +
                distance
            )

        )


        news_list.append(

            {

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

            }

        )


    return news_list


# =========================================================
# Keyword Retrieval
# =========================================================

def retrieve_keyword(

    query,

    limit=10,

    category=None,

    source=None

):

    keywords = extract_keywords(

        query

    )


    if not keywords:

        return []


    print(

        f"关键词检索: {keywords}"

    )


    keyword_count = (

        len(keywords)

    )


    all_results = []


    # -----------------------------------------------------
    # 每个关键词分别搜索
    # -----------------------------------------------------

    for keyword in keywords:

        rows = search_news(

            keyword,

            limit

        )


        for item in rows:

            news_id = item[0]


            # ---------------------------------------------
            # Metadata 过滤
            # ---------------------------------------------

            row_source = item[3]

            row_category = item[5]


            if source:

                if row_source != source:

                    continue


            if category:

                if row_category != category:

                    continue


            all_results.append(

                {

                    "id":
                        news_id,

                    "title":
                        item[1],

                    "url":
                        item[2],

                    "source":
                        row_source,

                    "summary":
                        item[4],

                    "category":
                        row_category,

                    "content":
                        "",

                    "distance":
                        None,

                    "vector_score":
                        0.0,

                    "keyword_score":
                        0.0,

                    "matched_keywords":
                        [keyword]

                }

            )


    if not all_results:

        return []


    # -----------------------------------------------------
    # 同一新闻去重
    #
    # 同一篇新闻可能命中：
    #
    # Gemini
    # Robotics
    #
    # 两个关键词
    # -----------------------------------------------------

    unique_results = {}


    for item in all_results:

        news_id = item["id"]


        if news_id not in unique_results:

            unique_results[news_id] = item

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


    # -----------------------------------------------------
    # 计算 Keyword Score
    #
    # 命中：
    #
    # 1 / 2 → 0.5
    # 2 / 2 → 1.0
    #
    # -----------------------------------------------------

    for item in unique_results.values():

        matched_count = (

            len(

                item[
                    "matched_keywords"
                ]

            )

        )


        item["keyword_score"] = (

            matched_count

            /

            keyword_count

        )


    # -----------------------------------------------------
    # 按 Keyword Score 排序
    # -----------------------------------------------------

    results = list(

        unique_results.values()

    )


    results.sort(

        key=lambda item:

            item[
                "keyword_score"
            ],

        reverse=True

    )


    return results[:limit]


# =========================================================
# Hybrid Retrieval
# =========================================================

def retrieve_news(

    query,

    limit=5,

    category=None,

    source=None

):

    query = query.strip()


    if not query:

        return []


    # -----------------------------------------------------
    # Vector Retrieval
    # -----------------------------------------------------

    vector_results = retrieve_vector(

        query=query,

        limit=max(

            limit * 5,

            10

        ),

        category=category,

        source=source

    )


    # -----------------------------------------------------
    # Keyword Retrieval
    # -----------------------------------------------------

    keyword_results = retrieve_keyword(

        query=query,

        limit=max(

            limit * 5,

            10

        ),

        category=category,

        source=source

    )


    # -----------------------------------------------------
    # 合并
    # -----------------------------------------------------

    merged = {}


    # -----------------------------------------------------
    # Vector Results
    # -----------------------------------------------------

    for item in vector_results:

        news_id = item["id"]


        if news_id not in merged:

            merged[news_id] = item

        else:

            # 同一新闻如果出现多个 Chunk，
            # 保留最好的 vector score

            if (

                item["vector_score"]

                >

                merged[
                    news_id
                ][
                    "vector_score"
                ]

            ):

                merged[
                    news_id
                ][
                    "vector_score"
                ] = item[
                    "vector_score"
                ]


    # -----------------------------------------------------
    # Keyword Results
    # -----------------------------------------------------

    for item in keyword_results:

        news_id = item["id"]


        if news_id not in merged:

            merged[news_id] = item


        else:

            merged[
                news_id
            ][
                "keyword_score"
            ] = item[
                "keyword_score"
            ]


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


    # =====================================================
    # Metadata Score
    # =====================================================

    for item in merged.values():

        metadata_score = 0.0


        # 指定分类并且匹配

        if category:

            if (

                item.get(
                    "category"
                )

                ==

                category

            ):

                metadata_score += 0.5


        # 指定来源并且匹配

        if source:

            if (

                item.get(
                    "source"
                )

                ==

                source

            ):

                metadata_score += 0.5


        item["metadata_score"] = (

            metadata_score

        )


    # =====================================================
    # Hybrid Score
    # =====================================================

    for item in merged.values():

        vector_score = item.get(

            "vector_score",

            0.0

        )


        keyword_score = item.get(

            "keyword_score",

            0.0

        )


        metadata_score = item.get(

            "metadata_score",

            0.0

        )


        # -------------------------------------------------
        # 当前版本权重
        #
        # Vector   60%
        # Keyword  30%
        # Metadata 10%
        # -------------------------------------------------

        item["hybrid_score"] = (

            0.6
            *
            vector_score

            +

            0.3
            *
            keyword_score

            +

            0.1
            *
            metadata_score

        )


    # -----------------------------------------------------
    # 排序
    # -----------------------------------------------------

    results = list(

        merged.values()

    )


    results.sort(

        key=lambda item:

            item[
                "hybrid_score"
            ],

        reverse=True

    )


    # -----------------------------------------------------
    # Top-K
    # -----------------------------------------------------

    return results[:limit]
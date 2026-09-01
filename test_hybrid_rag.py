# test_hybrid_rag.py

from src.rag.retriever import (
    retrieve_news,
    extract_keywords
)


def test_query(

    query,

    category=None,

    source=None

):

    print(
        "\n" + "=" * 70
    )

    print(
        "查询:",
        query
    )

    print(
        "关键词:",
        extract_keywords(query)
    )

    print(
        "Category Filter:",
        category
    )

    print(
        "Source Filter:",
        source
    )


    results = retrieve_news(

        query=query,

        limit=3,

        category=category,

        source=source

    )


    if not results:

        print(
            "没有找到结果。"
        )

        return


    for index, result in enumerate(

        results,

        start=1

    ):

        print(
            f"\n{index}. {result['title']}"
        )

        print(
            f"来源: {result['source']}"
        )

        print(
            f"分类: {result['category']}"
        )

        print(
            f"Vector Score: "
            f"{result.get('vector_score', 0):.4f}"
        )

        print(
            f"Keyword Score: "
            f"{result.get('keyword_score', 0):.4f}"
        )

        print(
            f"Metadata Score: "
            f"{result.get('metadata_score', 0):.4f}"
        )

        print(
            f"Hybrid Score: "
            f"{result.get('hybrid_score', 0):.4f}"
        )

        print(
            f"命中关键词: "
            f"{result.get('matched_keywords', [])}"
        )


def main():

    # =====================================================
    # 普通机器人问题
    # =====================================================

    test_query(

        "机器人最近有什么重要进展？"

    )


    # =====================================================
    # 带分类
    # =====================================================

    test_query(

        "最近有哪些重要的大模型进展？",

        category="大模型"

    )


    # =====================================================
    # 来源 + 分类
    # =====================================================

    test_query(

        "Anthropic 最近有哪些大模型进展？",

        category="大模型",

        source="Anthropic"

    )


    # =====================================================
    # Gemini Robotics
    # =====================================================

    test_query(

        "Gemini Robotics 最近有什么进展？"

    )


if __name__ == "__main__":

    main()
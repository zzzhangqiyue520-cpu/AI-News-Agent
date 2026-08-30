# test_hybrid_rag.py

from src.rag.retriever import (
    retrieve_news,
    extract_keywords
)


def main():

    queries = [

        "机器人最近有什么重要进展？",

        "Google在具身智能方面有什么研究？",

        "机器人如何实现全身控制？",

        "最近有哪些大模型相关消息？",

        "Gemini Robotics 最近有什么进展？",

        "Anthropic 最近有什么新闻？"

    ]


    for query in queries:

        print(
            "\n" + "=" * 70
        )


        print(
            "查询:",
            query
        )


        print(
            "提取关键词:",
            extract_keywords(query)
        )


        results = retrieve_news(

            query,

            limit=3

        )


        if not results:

            print(
                "没有找到相关新闻。"
            )

            continue


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
                f"{result['vector_score']:.4f}"
            )


            print(
                f"Keyword Score: "
                f"{result['keyword_score']:.4f}"
            )


            print(
                f"Hybrid Score: "
                f"{result['hybrid_score']:.4f}"
            )


            print(
                f"命中关键词: "
                f"{result.get('matched_keywords', [])}"
            )


if __name__ == "__main__":

    main()
# test_vector_rag.py

from src.rag.retriever import (
    retrieve_news
)


def main():

    queries = [

        "机器人最近有什么重要进展？",

        "Google在具身智能方面有什么研究？",

        "机器人如何实现全身控制？",

        "最近有哪些大模型相关消息？"

    ]


    for query in queries:

        print(
            "\n" + "=" * 60
        )


        print(
            "查询:",
            query
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
                f"距离: {result['distance']}"
            )


if __name__ == "__main__":

    main()
from src.rag.chunker import split_text


def main():

    text = (
        "这是一个用于测试文本切分的新闻。"
        "Gemini Robotics 2 是一个机器人模型。"
        "它支持全身控制、精细操作和多机器人协作。"
        "同时还包含安全机制和快速适配能力。"
        "这里继续添加一些文字，用来模拟比较长的新闻正文。"
        "我们希望观察文本是否能够被正确切分成多个Chunk。"
    )


    chunks = split_text(
        text,
        chunk_size=100,
        overlap=20
    )


    print(
        f"总 Chunk 数量: {len(chunks)}"
    )


    for index, chunk in enumerate(
        chunks
    ):

        print(
            "\n" + "=" * 40
        )

        print(
            f"Chunk {index}"
        )

        print(
            chunk
        )

        print(
            f"字符数: {len(chunk)}"
        )


if __name__ == "__main__":

    main()
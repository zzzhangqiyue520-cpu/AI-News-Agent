# src/rag/chunker.py


def split_text(
    text,
    chunk_size=1000,
    overlap=200
):
    """
    将长文本切分成多个 Chunk。

    chunk_size:
        每个 Chunk 最大字符数

    overlap:
        相邻 Chunk 重叠字符数

    例如：

    Chunk1:
    0 ~ 1000

    Chunk2:
    800 ~ 1800

    Chunk3:
    1600 ~ 2600
    """

    text = text.strip()


    if not text:

        return []


    if chunk_size <= 0:

        raise ValueError(
            "chunk_size 必须大于 0"
        )


    if overlap < 0:

        raise ValueError(
            "overlap 不能小于 0"
        )


    if overlap >= chunk_size:

        raise ValueError(
            "overlap 必须小于 chunk_size"
        )


    chunks = []


    start = 0

    text_length = len(text)


    step = (
        chunk_size
        - overlap
    )


    while start < text_length:

        end = min(
            start + chunk_size,
            text_length
        )


        chunk = text[
            start:end
        ].strip()


        if chunk:

            chunks.append(
                chunk
            )


        start += step


    return chunks
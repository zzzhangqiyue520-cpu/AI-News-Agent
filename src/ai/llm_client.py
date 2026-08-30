# src/ai/llm_client.py

from openai import OpenAI
from dotenv import load_dotenv

import os


load_dotenv()


client = OpenAI(
    api_key=os.getenv(
        "DEEPSEEK_API_KEY"
    ),
    base_url="https://api.deepseek.com",
    timeout=60,
    max_retries=3
)


def ask_llm(
    prompt=None,
    messages=None,
    tools=None
):
    """
    统一的大模型调用接口。

    两种使用方式：

    1. 普通文本调用
       ask_llm(prompt)

    2. Agent Tool Calling
       ask_llm(
           messages=messages,
           tools=TOOLS
       )
    """

    # ==========================================
    # 情况1：传入普通 prompt
    # ==========================================

    if messages is None:

        if prompt is None:

            raise ValueError(
                "prompt 和 messages 不能同时为空"
            )


        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]


    # ==========================================
    # 情况2：已经传入 messages
    # ==========================================

    request = {

        "model": "deepseek-chat",

        "messages": messages,

        "temperature": 0.3

    }


    # ==========================================
    # Tool Calling
    # ==========================================

    if tools:

        request["tools"] = tools

        request["tool_choice"] = "auto"


    response = client.chat.completions.create(
        **request
    )


    return response
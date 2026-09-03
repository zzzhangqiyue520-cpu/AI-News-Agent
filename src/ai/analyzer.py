# 负责新闻分析

from .llm_client import ask_llm

import json


def create_prompt(news):

    prompt = f"""

你是一名专业的AI科技新闻编辑。

你的任务：

分析下面这篇新闻。

新闻标题：

{news['title']}

新闻内容：

{news['content']}

要求：

1. 生成100字以内中文摘要

2. 提取3个关键词

3. 判断新闻分类

分类只能选择：

- AI技术
- 机器人
- 大模型
- 开源
- 科研
- 企业动态
- 其他

严格按照JSON格式返回。

不要输出：

Markdown
代码块
解释文字

返回格式：

{{
    "summary":"",
    "keywords":[],
    "category":""
}}

"""

    return prompt


def summarize(news):

    prompt = create_prompt(news)

    response = ask_llm(prompt)

    try:

        # =================================================
        # 从 ChatCompletion 中获取真正的文本内容
        # =================================================

        result = response.choices[0].message.content

        if not result:

            raise ValueError(
                "LLM 返回的 content 为空"
            )

        # =================================================
        # 防止模型返回 ```json
        # =================================================

        result = result.replace(
            "```json",
            ""
        )

        result = result.replace(
            "```",
            ""
        )

        # =================================================
        # JSON 解析
        # =================================================

        analysis = json.loads(
            result.strip()
        )

        # =================================================
        # 基本格式检查
        # =================================================

        if not isinstance(analysis, dict):

            raise ValueError(
                "LLM 返回的 JSON 不是对象"
            )

        if "summary" not in analysis:

            raise ValueError(
                "LLM 返回结果缺少 summary"
            )

        if "keywords" not in analysis:

            raise ValueError(
                "LLM 返回结果缺少 keywords"
            )

        if "category" not in analysis:

            raise ValueError(
                "LLM 返回结果缺少 category"
            )

        return analysis

    except Exception as e:

        print(
            "AI JSON解析失败:",
            e
        )

        print(
            "原始返回:",
            response
        )

        return {
            "summary": "",
            "keywords": [],
            "category": "其他"
        }


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


    result = ask_llm(prompt)



    try:


        # 防止模型返回 ```json

        result = result.replace(
            "```json",
            ""
        )

        result = result.replace(
            "```",
            ""
        )


        analysis = json.loads(
            result.strip()
        )


        return analysis



    except Exception as e:


        print(
            "AI JSON解析失败:",
            e
        )


        print(
            "原始返回:",
            result
        )


        return {

            "summary":"",
            "keywords":[],
            "category":"其他"

        }
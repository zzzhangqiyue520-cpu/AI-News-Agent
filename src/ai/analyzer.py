#负责：新闻分析
#角色“你是谁” + 任务“做什么” + 输入“提供数据” + 限制“限制输出” + 输出格式“返回什么结构”

from .llm_client import ask_llm
def create_prompt(news):

    prompt = f"""
    你是一名专业的AI科技新闻编辑。

    任务：
    请分析下面这篇新闻。
    
    新闻标题：
    {news['title']}
    新闻内容：
    {news['content']}
    
    要求：
    1. 生成100字以内摘要
    2. 提取3个关键词
    3. 判断新闻所属类别
    
    请按照以下格式输出：
    摘要：
    关键词：
    分类：
    """

    return prompt

def summarize(news):

    prompt=create_prompt(news)

    result=ask_llm(prompt)

    return result
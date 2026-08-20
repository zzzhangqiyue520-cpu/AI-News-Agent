from src.agent.tools import (
    search_latest_news,
    search_category_news,
    search_keyword
)


from src.ai.llm_client import ask_llm




def select_tool(question):


    question = question.lower()



    if "机器人" in question:


        return search_category_news(
            "机器人"
        )


    elif "gemini" in question:


        return search_keyword(
            "Gemini"
        )


    elif "claude" in question:


        return search_keyword(
            "Claude"
        )


    else:


        return search_latest_news()





def run_agent(question):


    print(
        "用户问题:",
        question
    )


    news = select_tool(
        question
    )


    print(
        "检索到新闻:",
        len(news)
    )



    prompt=f"""

你是AI新闻助手。


用户问题：

{question}



数据库新闻：

{news}



请总结回答。


要求：

1. 只能使用提供新闻

2. 不编造

3. 中文回答


"""


    answer = ask_llm(
        prompt
    )


    return answer
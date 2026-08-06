#负责：和模型通信
#输入:prompt文本;输出:模型回复

def ask_llm(prompt):

    print("发送给LLM的内容:")
    print(prompt)

    response = "这里是模型返回结果"

    return response
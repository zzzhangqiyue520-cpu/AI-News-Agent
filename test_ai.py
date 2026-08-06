from src.ai.analyzer import summarize

news = {
    "title": "OpenAI发布新模型",
    "content": "OpenAI今天发布了一款新的人工智能模型，提高了模型推理能力。"
}

result = summarize(news)

print("AI结果:")
print(result)
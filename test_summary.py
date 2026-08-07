from src.news_manager import NewsManager
from src.ai.analyzer import summarize


manager = NewsManager("data/news.json")


news_list = manager.load_news()


for news in news_list:

    result = summarize(news)

    print("新闻标题:")
    print(news["title"])

    print("AI分析结果:")
    print(result)

    print("----------------")
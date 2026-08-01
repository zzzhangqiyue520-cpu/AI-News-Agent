from src.news_manager import NewsManager

def main():
    print("AI-News-Agent启动")

    manager = NewsManager(
        "data/news.json"
    )

    manager.add_news(
        "AI发展趋势",
        "人工智能正在快速发展"
    )

    news = manager.load_news()

    for item in news:
        print("----------------")
        print(item["title"])
        print(item["content"])

if __name__ == "__main__":
    main()

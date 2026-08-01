from src.crawler import crawl
from src.utils import save_news

def main():
    print("AI-News-Agent启动")
    news = crawl()
    save_news(news)

if __name__ == "__main__":
    main()

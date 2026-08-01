def crawl():

    try:
        print("开始抓取AI新闻")

        news = [
            {
                "title":"AI新闻1"
            },
            {
                "title":"AI新闻2"
            }
        ]
        
        return news

    except Exception as e:
        print("爬取失败:", e)

        return []

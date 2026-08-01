import json
import os

class NewsManager:
    def __init__(self,filepath):
        self.filepath = filepath

    def save_news(self,news_list):
        try:
            with open(self.filepath,"w",encoding="utf-8") as f:
                json.dump(news_list,f,ensure_ascii=False,indent=4)

        except Exception as e:
            print("保存失败",e)

    def load_news(self):
        try:
            if not os.path.exists(self.filepath):
                return []

            with open(self.filepath,"r",encoding="utf-8") as f:
                return json.load(f)

        except Exception as e:
            print("读取失败",e)
            return []

    def add_news(self,title,content):
        news_list = self.load_news()

        news = {
            "title":title,
            "content":content
        }

        news_list.append(news)
        self.save_news(news_list)
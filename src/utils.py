import datetime
import json

def get_time():
    return datetime.datetime.now()

def save_text(filename, text):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(text)

        print("保存成功")

    except Exception as e:
        print("保存失败:", e)

def save_news(news):
    try:
        with open("data/news.json","w",encoding="utf-8") as f:

            json.dump(
                news,
                f,
                ensure_ascii=False,
                indent=4
            )

        print("新闻保存成功")
        return True

    except Exception as e:
        print("新闻保存失败:", e)
        return False
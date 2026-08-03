import requests

def crawl():

    try:
        print("开始抓取AI新闻")

        url = "https://www.people.com.cn"

        resp = requests.get(url)

        resp.encoding = "utf-8"

        html = resp.text

        return html

    except Exception as e:
        print("爬取失败:", e)

        return None

if __name__ == "__main__":
    crawl()

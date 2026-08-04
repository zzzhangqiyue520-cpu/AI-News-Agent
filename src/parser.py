from bs4 import BeautifulSoup
from utils import get_time

def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    news = []

    items = soup.find_all("tr",attrs={"class":"athing submission"})

    for item in items:

        span = item.find("span",attrs={"class":"titleline"})

        if span:
            a = span.find("a")

            title = a.text.strip()

            url = a.get("href")

            news.append(
                {
                    "title":title,
                    "url":url,
                    "time":str(get_time())
                }
            )
    return news





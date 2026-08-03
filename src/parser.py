from bs4 import BeautifulSoup

def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    news = []

    items = soup.find_all("div",attrs={"class":"news-item"})

    for item in items:

        a = item.find("a")

        if a:
            title = a.text.strip()

            url = a.get("href")

            news.append(
                {
                    "title":title,
                    "url":url
                }
            )
    return news



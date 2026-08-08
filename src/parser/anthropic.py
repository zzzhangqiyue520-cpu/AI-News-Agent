from bs4 import BeautifulSoup

def parse_anthropic(html):

    soup = BeautifulSoup(html, "html.parser")

    news = []

    articles = soup.find_all("div",attrs={"class": "article-list-item"})

    for article in articles:

        title_tag = article.find("h3")

        link_tag = article.find("a",href=True)

        if not title_tag or not link_tag:
            continue

        url = link_tag["href"]

        # 过滤非新闻
        if "/news/" not in url:
            continue

        news.append(
            {
                "title": title_tag.text.strip(),
                "url": url,
                "source": "Anthropic",
                "time": "",
                "content": ""
            }
            )

    return news
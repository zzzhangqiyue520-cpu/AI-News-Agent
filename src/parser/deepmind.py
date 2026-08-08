from bs4 import BeautifulSoup


def parse_deepmind(html):

    soup = BeautifulSoup(html, "html.parser")

    news = []

    articles = soup.find_all("article",attrs={"class": "card-blog"})

    for article in articles:

        # 标题
        title_tag = article.find("h3",attrs={"class": "card__title"})

        # 链接
        link_tag = article.find("a")

        # 时间
        time_tag = article.find("time")


        if title_tag and link_tag:

            url = link_tag.get("href")

            # DeepMind链接是相对路径
            if url.startswith("/"):
                url = "https://deepmind.google" + url


            news.append(
                {
                    "title": title_tag.text.strip(),
                    "url": url,
                    "source": "DeepMind",
                    "time": time_tag.text.strip()
                    if time_tag
                    else "",
                    "content": ""
                }
            )


    return news
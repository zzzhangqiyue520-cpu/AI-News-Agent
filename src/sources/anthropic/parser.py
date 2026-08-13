from lxml import etree
from bs4 import BeautifulSoup



def parse_rss(xml_text):


    root = etree.fromstring(
        xml_text.encode("utf-8")
    )


    news_list = []


    items = root.xpath(
        "//item"
    )


    for item in items:


        title = item.xpath(
            "./title/text()"
        )


        url = item.xpath(
            "./link/text()"
        )


        time = item.xpath(
            "./pubDate/text()"
        )


        # 关键修改
        description = item.xpath(
            "./description/text()"
        )


        content = ""



        if description:


            html = description[0]


            soup = BeautifulSoup(
                html,
                "html.parser"
            )



            paragraphs = []



            for p in soup.find_all(
                [
                    "p",
                    "h2",
                    "h3"
                ]
            ):


                text = p.get_text(
                    " ",
                    strip=True
                )


                if text:

                    paragraphs.append(
                        text
                    )



            content = "\n\n".join(
                paragraphs
            )



        news = {


            "title":
            title[0].strip()
            if title else "",


            "url":
            url[0].strip()
            if url else "",


            "source":
            "Anthropic",


            "time":
            time[0].strip()
            if time else "",


            "content":
            content

        }



        news_list.append(
            news
        )



    return news_list
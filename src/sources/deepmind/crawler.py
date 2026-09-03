import aiohttp
import asyncio


from bs4 import BeautifulSoup


from src.config import (
    USER_AGENT,
    REQUEST_TIMEOUT
)



class DeepMindCrawler:


    def __init__(self):

        self.url = (
            "https://deepmind.google/blog/"
        )


        self.headers = {

            "User-Agent":
            USER_AGENT

        }


        self.timeout = aiohttp.ClientTimeout(
            total=REQUEST_TIMEOUT
        )

    async def fetch_html(
            self,
            url
    ):

        max_retries = 3

        for attempt in range(
                1,
                max_retries + 1
        ):

            try:

                async with aiohttp.ClientSession(
                        timeout=self.timeout
                ) as session:

                    async with session.get(
                            url,
                            headers=self.headers
                    ) as response:
                        print(
                            "请求状态:",
                            response.status
                        )

                        if response.status != 200:
                            raise RuntimeError(
                                f"HTTP {response.status}"
                            )

                        return await response.text()

            except (
                    aiohttp.ClientError,
                    asyncio.TimeoutError,
                    RuntimeError
            ) as e:

                print(
                    f"请求失败，第{attempt}次尝试: "
                    f"{url}"
                )

                print(
                    "错误:",
                    e
                )

                if attempt < max_retries:

                    await asyncio.sleep(
                        2
                    )

                else:

                    print(
                        f"请求最终失败: {url}"
                    )

                    return None

    async def crawl(self):

        html = await self.fetch_html(
            self.url
        )

        if not html:
            print(
                "DeepMind 页面获取失败，本次跳过。"
            )

            return []

        soup = BeautifulSoup(
            html,
            "html.parser"
        )


        news_list = []


        articles = soup.find_all(
            "article",
            class_="card-blog"
        )


        print(
            "找到article:",
            len(articles)
        )



        for article in articles:


            title_tag = article.find(
                "h3"
            )


            link_tag = article.find(
                "a",
                href=True
            )


            time_tag = article.find(
                "time"
            )


            if not title_tag or not link_tag:

                continue



            title = title_tag.get_text(
                strip=True
            )


            url = link_tag["href"]



            if url.startswith("/"):

                url = (
                    "https://deepmind.google"
                    +
                    url
                )



            # 过滤非DeepMind文章
            if (
                "deepmind.google"
                not in url
            ):

                continue



            time = ""


            if time_tag:

                time = time_tag.get_text(
                    strip=True
                )



            news_list.append(
                {
                    "title": title,
                    "url": url,
                    "time": time
                }
            )



        return news_list
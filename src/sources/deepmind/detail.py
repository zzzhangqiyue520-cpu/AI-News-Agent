import asyncio
import aiohttp

from bs4 import BeautifulSoup


from src.config import (
    USER_AGENT,
    REQUEST_TIMEOUT
)



class DeepMindDetail:


    def __init__(self):

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


        for attempt in range(3):

            try:


                async with aiohttp.ClientSession(
                    timeout=self.timeout
                ) as session:


                    async with session.get(
                        url,
                        headers=self.headers
                    ) as response:


                        print(
                            "文章状态:",
                            response.status
                        )


                        if response.status != 200:

                            return ""


                        return await response.text()



            except asyncio.TimeoutError:


                print(
                    f"请求超时，第{attempt + 1}次尝试:",
                    url
                )


                await asyncio.sleep(2)



            except Exception as e:


                print(
                    f"请求失败，第{attempt + 1}次尝试:",
                    url
                )


                print(
                    "错误:",
                    e
                )


                await asyncio.sleep(2)



        print(
            "最终请求失败:",
            url
        )


        return ""




    async def parse_content(
            self,
            url
    ):


        html = await self.fetch_html(
            url
        )


        if not html:

            return ""



        soup = BeautifulSoup(
            html,
            "html.parser"
        )



        # 获取所有正文区域
        content_blocks = soup.find_all(
            "div",
            class_="rich-text"
        )


        if not content_blocks:

            return ""



        paragraphs = []



        for block in content_blocks:



            elements = block.find_all(
                [
                    "h2",
                    "p",
                    "li"
                ]
            )


            for element in elements:


                text = element.get_text(
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



        return content
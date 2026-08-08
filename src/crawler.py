import aiohttp
import asyncio
import time

async def fetch(session,url):

    timeout = aiohttp.ClientTimeout(total=5)

    headers = {
        "User-Agent":"Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36"
    }

    try:

        async with session.get(url,timeout=timeout,headers=headers) as resp:

            html = await resp.text()

            print(url,"完成")

            return html

    except Exception as e:

        print(url,"失败",e)

        return None

async def crawl():

    websites = [

        {
            "source":"Anthropic",
            "url":"https://www.anthropic.com/"
        },

        {
            "source":"DeepMind",
            "url":"https://deepmind.google/blog/"
        }

    ]


    async with aiohttp.ClientSession() as session:

        tasks = []

        for site in websites:

            tasks.append(
                fetch(
                    session,
                    site["url"]
                )
            )


        html_list = await asyncio.gather(*tasks)

        results = []

        for site, html in zip(websites, html_list):

            if html:

                results.append(
                    {
                        "source":site["source"],
                        "html":html
                    }
                )


        return results
    

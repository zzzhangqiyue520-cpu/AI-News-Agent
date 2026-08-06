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
    urls = [
        "https://news.ycombinator.com",

        "https://openai.com/news/",

        "https://deepmind.google/discover/blog/"
    ]

    async with aiohttp.ClientSession() as session:

        tasks = []

        for url in urls:

            tasks.append(fetch(session,url))

        result = await asyncio.gather(*tasks)

        return result

start = time.time()

results = asyncio.run(crawl())


for r in results:

    if r:

        print(r[:200])

end = time.time()

print("耗时",end-start)

import aiohttp


RSS_URL = "https://rsshub.bestblogs.dev/anthropic/news"



async def fetch_rss():

    headers = {

        "User-Agent":
        "Mozilla/5.0"

    }


    timeout = aiohttp.ClientTimeout(
        total=30
    )


    async with aiohttp.ClientSession(
        timeout=timeout
    ) as session:


        async with session.get(
            RSS_URL,
            headers=headers
        ) as response:


            print(
                "Anthropic RSS状态:",
                response.status
            )


            return await response.text()
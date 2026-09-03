import asyncio
import aiohttp


RSS_URL = "https://rsshub.bestblogs.dev/anthropic/news"


async def fetch_rss():

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    timeout = aiohttp.ClientTimeout(
        total=30
    )

    max_retries = 3

    for attempt in range(1, max_retries + 1):

        try:

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
                f"Anthropic RSS请求失败，"
                f"第{attempt}次尝试: {e}"
            )

            if attempt < max_retries:

                await asyncio.sleep(
                    2
                )

            else:

                print(
                    "Anthropic RSS获取失败，"
                    "本次跳过。"
                )

                return None
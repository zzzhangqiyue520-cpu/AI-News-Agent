#总调度器

from sources.deepmind.crawler import crawl_deepmind
from sources.anthropic.crawler import crawl_anthropic


async def crawl():

    results = []


    deepmind_news = await crawl_deepmind()

    results.extend(
        deepmind_news
    )


    anthropic_news = await crawl_anthropic()

    results.extend(
        anthropic_news
    )


    return results
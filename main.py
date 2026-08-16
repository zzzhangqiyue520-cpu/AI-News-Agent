import asyncio


from src.sources.deepmind.source import DeepMindSource
from src.sources.anthropic.source import AnthropicSource


from src.ai.analyzer import summarize


from src.utils import generate_id


from src.database.database import (
    create_table,
    exists_news,
    save_news,
    get_latest_news
)





SOURCES = [

    DeepMindSource(),

    AnthropicSource()

]







def analyze_news(news):


    print(
        "开始 AI 分析:",
        news["title"]
    )


    try:


        return summarize(
            news
        )


    except Exception as e:


        print(
            "AI失败:",
            e
        )


        return {

            "summary":"",

            "keywords":[],

            "category":"其他"

        }







async def main():


    print(
        "====== AI News Agent ======"
    )



    # 创建数据库

    create_table()



    latest_news=[]



    # =====================
    # 1. 获取新闻
    # =====================


    for source in SOURCES:


        try:


            news_list = await source.fetch()


            latest_news.extend(
                news_list
            )


        except Exception as e:


            print(
                source.name,
                "失败:",
                e
            )



    print(

        "\n抓取新闻数量:",

        len(latest_news)

    )





    new_count=0

    duplicate_count=0




    # =====================
    # 2. 去重
    # =====================


    for news in latest_news:



        news_id = generate_id(

            news["url"]

        )


        news["id"] = news_id




        if exists_news(news_id):


            print(

                "重复新闻，跳过:",

                news["title"]

            )


            duplicate_count+=1


            continue





        # =====================
        # 3. AI分析
        # =====================


        news["analysis"] = analyze_news(

            news

        )





        # =====================
        # 4. 保存数据库
        # =====================


        save_news(

            news

        )



        print(

            "保存新闻:",

            news["title"]

        )



        new_count+=1





    print("\n======运行完成======")

    print(

        "新增:",

        new_count

    )

    print(

        "重复:",

        duplicate_count

    )





    print(

        "\n最新新闻:"
    )


    for item in get_latest_news(5):


        print(item)







if __name__=="__main__":


    asyncio.run(
        main()
    )
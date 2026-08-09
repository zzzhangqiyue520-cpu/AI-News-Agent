from datetime import datetime




def parse_news(
        item
):


    return {


        "title":
            item.get(
                "title",
                ""
            ),



        "url":
            item.get(
                "url",
                ""
            ),



        "source":
            "DeepMind",



        "time":
            item.get(
                "time",
                datetime.now()
                .strftime(
                    "%Y-%m-%d"
                )
            ),



        # 原始正文
        "content":
            item.get(
                "content",
                ""
            ),



        # AI阶段使用
        "summary":
            "",



        "keywords":
            [],



        "category":
            ""

    }
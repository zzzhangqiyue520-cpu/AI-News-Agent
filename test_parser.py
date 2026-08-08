from src.parser.deepmind import parse_deepmind
from src.parser.anthropic import parse_anthropic


# 测试 DeepMind
def test_deepmind():

    with open(
        "data/deepmind.html",
        "r",
        encoding="utf-8"
    ) as f:

        html = f.read()


    news = parse_deepmind(html)


    print("====== DeepMind ======")

    print("新闻数量:", len(news))


    for item in news[:3]:

        print("----------------")

        print("标题:", item["title"])
        print("链接:", item["url"])
        print("来源:", item["source"])
        print("时间:", item["time"])



# 测试 Anthropic
def test_anthropic():

    with open(
        "data/anthropic.html",
        "r",
        encoding="utf-8"
    ) as f:

        html = f.read()


    news = parse_anthropic(html)


    print("\n====== Anthropic ======")

    print("新闻数量:", len(news))


    for item in news[:3]:

        print("----------------")

        print("标题:", item["title"])
        print("链接:", item["url"])
        print("来源:", item["source"])
        print("时间:", item["time"])



if __name__ == "__main__":

    test_deepmind()

    test_anthropic()
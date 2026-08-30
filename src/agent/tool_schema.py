# src/agent/tool_schema.py


TOOLS = [

    {
        "type": "function",

        "function": {
            "name": "search_latest_news",

            "description":
                "查询数据库中最近发布的AI新闻。当用户询问最近、最新、近期AI新闻时使用。",

            "parameters": {
                "type": "object",

                "properties": {
                    "limit": {
                        "type": "integer",
                        "description":
                            "返回新闻数量，建议1到10条。"
                    }
                },

                "required": [
                    "limit"
                ]
            }
        }
    },


    {
        "type": "function",

        "function": {
            "name": "search_category_news",

            "description":
                "根据新闻分类查询相关新闻，例如机器人、大模型、开源、科研、企业动态等。",

            "parameters": {
                "type": "object",

                "properties": {
                    "category": {
                        "type": "string",
                        "description":
                            "新闻分类，例如机器人、大模型、开源、科研、企业动态。"
                    }
                },

                "required": [
                    "category"
                ]
            }
        }
    },


    {
        "type": "function",

        "function": {
            "name": "search_source_news",

            "description":
                "根据新闻来源查询相关新闻。例如 DeepMind、Anthropic。",

            "parameters": {
                "type": "object",

                "properties": {
                    "source": {
                        "type": "string",
                        "description":
                            "新闻来源，例如 DeepMind 或 Anthropic。"
                    }
                },

                "required": [
                    "source"
                ]
            }
        }
    },


    {
        "type": "function",

        "function": {
            "name": "search_keyword",

            "description":
                "根据关键词搜索新闻。例如 Gemini、Claude、Robotics。",

            "parameters": {
                "type": "object",

                "properties": {
                    "keyword": {
                        "type": "string",
                        "description":
                            "要搜索的关键词。"
                    }
                },

                "required": [
                    "keyword"
                ]
            }
        }
    },


    {
        "type": "function",

        "function": {
            "name": "get_news_detail",

            "description":
                "根据新闻ID读取该新闻的完整正文内容，用于深入阅读和分析某一篇新闻。通常应先使用搜索工具找到目标新闻，再调用该工具读取完整正文。",

            "parameters": {
                "type": "object",

                "properties": {
                    "news_id": {
                        "type": "integer",
                        "description":
                            "数据库中新闻的ID。"
                    }
                },

                "required": [
                    "news_id"
                ]
            }
        }
    }

]
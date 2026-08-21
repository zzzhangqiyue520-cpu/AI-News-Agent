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
                        "description": "返回的新闻数量，建议1到10条。"
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
                "根据关键词搜索新闻标题、摘要或分类。例如 Gemini、Claude、Robotics。",

            "parameters": {
                "type": "object",

                "properties": {
                    "keyword": {
                        "type": "string",
                        "description":
                            "需要搜索的关键词。"
                    }
                },

                "required": [
                    "keyword"
                ]
            }
        }
    }

]
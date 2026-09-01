# src/agent/tool_schema.py


TOOLS = [

    # =====================================================
    # 最新新闻
    # =====================================================

    {
        "type": "function",

        "function": {
            "name": "search_latest_news",

            "description": (
                "查询数据库中最新发布的新闻列表。"
                "适用于用户明确询问“最近有哪些新闻”“最新新闻”“近期新闻”等问题。"
                "如果用户的问题只是获取最近新闻列表，使用该工具即可，"
                "不要为了补充信息而重复调用其他搜索工具。"
            ),

            "parameters": {
                "type": "object",

                "properties": {
                    "limit": {
                        "type": "integer",

                        "description": (
                            "返回新闻数量，"
                            "建议 5 到 10 条。"
                        )
                    }
                },

                "required": [
                    "limit"
                ]
            }
        }
    },


    # =====================================================
    # 分类新闻
    # =====================================================

    {
        "type": "function",

        "function": {
            "name": "search_category_news",

            "description": (
                "按照新闻分类查询新闻。"
                "适用于用户明确指定了新闻类别的问题，"
                "例如“机器人新闻”“大模型新闻”“开源新闻”“科研新闻”。"
                "如果用户已经明确指定分类，优先使用此工具，"
                "通常不需要再调用 search_latest_news 或 search_keyword。"
            ),

            "parameters": {
                "type": "object",

                "properties": {
                    "category": {
                        "type": "string",

                        "description": (
                            "新闻分类。"
                            "可选：AI技术、机器人、大模型、"
                            "开源、科研、企业动态、其他。"
                        )
                    }
                },

                "required": [
                    "category"
                ]
            }
        }
    },


    # =====================================================
    # 来源新闻
    # =====================================================

    {
        "type": "function",

        "function": {
            "name": "search_source_news",

            "description": (
                "按照新闻来源查询新闻。"
                "适用于用户明确询问某个机构或来源最近有哪些新闻，"
                "例如“Anthropic最近有什么新闻”“DeepMind最近有什么动态”。"
                "如果用户只指定了一个来源，通常使用此工具即可。"
            ),

            "parameters": {
                "type": "object",

                "properties": {
                    "source": {
                        "type": "string",

                        "description": (
                            "新闻来源，例如 DeepMind、Anthropic。"
                        )
                    }
                },

                "required": [
                    "source"
                ]
            }
        }
    },


    # =====================================================
    # 关键词搜索
    # =====================================================

    {
        "type": "function",

        "function": {
            "name": "search_keyword",

            "description": (
                "按照一个明确的关键词或实体搜索新闻。"
                "适用于用户询问某个具体模型、产品、人物或技术名称，"
                "例如 Gemini、Claude、Robotics、Gemma。"
                "如果用户的问题需要语义理解、背景分析或深入研究，"
                "优先使用 search_knowledge，而不是只使用此工具。"
            ),

            "parameters": {
                "type": "object",

                "properties": {
                    "keyword": {
                        "type": "string",

                        "description": (
                            "要搜索的明确关键词或实体名称。"
                        )
                    }
                },

                "required": [
                    "keyword"
                ]
            }
        }
    },


    # =====================================================
    # 知识库检索
    # =====================================================

    {
        "type": "function",

        "function": {
            "name": "search_knowledge",

            "description": (
                "从AI新闻知识库中进行深度语义检索。"
                "该工具内部使用 Hybrid Retrieval，"
                "结合 Chroma 向量检索和 SQLite 关键词检索。"
                "适用于需要解释、原因分析、技术细节、背景、意义、趋势或比较的问题。"
                "例如“为什么Gemini Robotics 2重要”“它是怎么实现全身控制的”。"
                "如果用户只是要求列出最近新闻，不要使用此工具。"
            ),

            "parameters": {
                "type": "object",

                "properties": {
                    "query": {
                        "type": "string",

                        "description": (
                            "用于知识库检索的问题或主题。"
                            "应尽量描述用户真正想了解的知识点。"
                        )
                    },

                    "limit": {
                        "type": "integer",

                        "description": (
                            "返回相关知识块数量，"
                            "建议 3 到 5。"
                        )
                    }
                },

                "required": [
                    "query",
                    "limit"
                ]
            }
        }
    },


    # =====================================================
    # 新闻详情
    # =====================================================

    {
        "type": "function",

        "function": {
            "name": "get_news_detail",

            "description": (
                "根据新闻ID读取单篇新闻的完整正文。"
                "只有当用户要求深入分析某一篇具体新闻，"
                "或者现有搜索结果不足以回答问题时才使用。"
                "不要对普通的新闻列表问题逐篇读取正文。"
            ),

            "parameters": {
                "type": "object",

                "properties": {
                    "news_id": {
                        "type": "integer",

                        "description": (
                            "数据库中的新闻ID。"
                        )
                    }
                },

                "required": [
                    "news_id"
                ]
            }
        }
    }

]
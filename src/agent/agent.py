# src/agent/agent.py

import json

from src.ai.llm_client import ask_llm

from src.agent.tools import (
    execute_tool
)

from src.agent.tool_schema import (
    TOOLS
)

from src.logger import logger


MAX_TOOL_ROUNDS = 5


def run_agent(question):

    logger.info(
        f"用户问题: {question}"
    )


    messages = [

        {
            "role": "system",

            "content": """
        你是一个专业的AI科技新闻研究助手。

        你的任务是根据用户问题，从新闻数据库和知识库中获取信息并回答。

        工具使用原则：

        1. 用户询问最近有哪些新闻时，可以使用 search_latest_news。
        2. 用户询问某个分类时，可以使用 search_category_news。
        3. 用户询问某个新闻来源时，可以使用 search_source_news。
        4. 用户询问特定关键词时，可以使用 search_keyword。
        5. 用户需要深入了解某个主题、技术、背景、意义、原因或趋势时，优先使用 search_knowledge。
        6. 用户要求深入分析某篇具体新闻时，可以先搜索新闻，再使用 get_news_detail 获取完整正文。
        7. 如果需要比较多个对象，可以调用多个工具。
        8. 可以连续调用多个工具。
        9. 根据工具返回结果决定下一步是否需要继续检索。
        10. 不要编造数据库或知识库中不存在的信息。
        11. 使用中文回答。
        """
        },

        {
            "role": "user",
            "content": question
        }

    ]


    # =====================================================
    # Agent循环
    # =====================================================

    for round_number in range(
        MAX_TOOL_ROUNDS
    ):

        logger.info(
            f"Agent第 {round_number + 1} 轮思考"
        )


        response = ask_llm(
            messages=messages,
            tools=TOOLS
        )


        message = (
            response
            .choices[0]
            .message
        )


        # =================================================
        # 没有工具调用
        # =================================================

        if not message.tool_calls:

            logger.info(
                "Agent决定直接回答"
            )

            return (
                message.content
                or ""
            )


        # =================================================
        # 保存assistant消息
        # =================================================

        messages.append(
            message
        )


        # =================================================
        # 执行所有工具
        # =================================================

        for tool_call in (
            message.tool_calls
        ):

            tool_name = (
                tool_call
                .function
                .name
            )


            arguments_text = (
                tool_call
                .function
                .arguments
            )


            logger.info(
                f"模型选择工具: {tool_name}"
            )


            logger.info(
                f"工具参数: {arguments_text}"
            )


            # ---------------------------------------------
            # 解析参数
            # ---------------------------------------------

            try:

                arguments = json.loads(
                    arguments_text
                )

            except json.JSONDecodeError as e:

                logger.error(
                    f"工具参数解析失败: {e}"
                )


                result = {
                    "error":
                        "工具参数不是合法JSON"
                }


                messages.append(
                    {
                        "role": "tool",

                        "tool_call_id":
                            tool_call.id,

                        "content":
                            json.dumps(
                                result,
                                ensure_ascii=False
                            )
                    }
                )


                continue


            # ---------------------------------------------
            # 执行工具
            # ---------------------------------------------

            try:

                result = execute_tool(
                    tool_name,
                    arguments
                )


                logger.info(
                    f"工具执行完成: {tool_name}"
                )


            except Exception as e:

                logger.exception(
                    f"工具执行失败: {tool_name}"
                )


                result = {
                    "error": str(e)
                }


            # ---------------------------------------------
            # 工具结果
            # ---------------------------------------------

            messages.append(
                {
                    "role": "tool",

                    "tool_call_id":
                        tool_call.id,

                    "content":
                        json.dumps(
                            result,
                            ensure_ascii=False
                        )
                }
            )


    # =====================================================
    # 超过最大工具调用轮数
    # =====================================================

    logger.warning(
        "Agent达到最大工具调用轮数"
    )


    return (
        "Agent执行步骤过多，"
        "暂时无法完成这个问题。"
    )
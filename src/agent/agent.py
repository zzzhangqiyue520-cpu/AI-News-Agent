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

你的任务是根据用户的问题，从新闻数据库中获取信息并进行分析。

你可以使用以下工具：

1. 搜索最新新闻
2. 按新闻分类搜索
3. 按新闻来源搜索
4. 按关键词搜索
5. 读取某篇新闻的完整正文

工作原则：

1. 需要数据库信息时，优先使用工具。
2. 如果搜索结果已经足够回答问题，可以直接回答。
3. 如果用户要求深入分析某篇新闻，应先搜索找到新闻ID，再读取完整正文。
4. 如果完整正文不足以回答问题，可以继续调用其他工具。
5. 可以连续调用多个工具。
6. 回答只能基于数据库和工具返回的信息。
7. 不要编造不存在的信息。
8. 使用中文回答。
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
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



def run_agent(
    question
):

    logger.info(
        f"用户问题: {question}"
    )


    messages = [

        {
            "role": "system",
            "content": """
        你是一个AI科技新闻助手。

        你的任务是根据用户问题，从新闻数据库中检索信息并回答。

        规则：

        1. 需要新闻数据时，必须优先使用工具。
        2. 可以根据问题选择一个或多个工具。
        3. 如果问题涉及多个新闻来源，可以调用多个工具。
        4. 如果问题涉及比较两个来源，可以分别查询两个来源后再进行比较。
        5. 不要编造数据库不存在的信息。
        6. 工具返回结果后，结合全部结果回答用户。
        7. 使用中文回答。
        8. 如果没有找到相关数据，明确告诉用户。
        """
        },

        {
            "role": "user",

            "content": question
        }

    ]


    # =====================================================
    # 第一次请求：让LLM决定是否调用工具
    # =====================================================

    response = ask_llm(
        messages=messages,
        tools=TOOLS
    )


    message = response.choices[0].message


    logger.info(
        f"模型首次返回: {message.content}"
    )


    # =====================================================
    # 没有调用工具
    # =====================================================

    if not message.tool_calls:

        return message.content or ""


    # =====================================================
    # 保存assistant的tool call消息
    # =====================================================

    messages.append(
        message
    )


    # =====================================================
    # 执行所有工具调用
    # =====================================================

    for tool_call in message.tool_calls:


        tool_name = (
            tool_call.function.name
        )


        arguments_text = (
            tool_call.function.arguments
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
                f"工具参数JSON解析失败: {e}"
            )


            tool_result = {
                "error": "工具参数不是合法JSON"
            }


            messages.append(
                {
                    "role": "tool",

                    "tool_call_id":
                        tool_call.id,

                    "content":
                        json.dumps(
                            tool_result,
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
        # 把工具结果交还给LLM
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
    # 第二次请求：让LLM根据工具结果回答
    # =====================================================

    final_response = ask_llm(
        messages=messages,
        tools=TOOLS
    )


    final_message = (
        final_response
        .choices[0]
        .message
    )


    logger.info(
        "Agent最终回答生成完成"
    )


    return final_message.content or ""
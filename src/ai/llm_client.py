# src/ai/llm_client.py


from openai import OpenAI

from dotenv import load_dotenv

import os



load_dotenv()



client = OpenAI(

    api_key=os.getenv(
        "DEEPSEEK_API_KEY"
    ),

    base_url="https://api.deepseek.com",

    timeout=60,

    max_retries=3
)



def ask_llm(
    messages,
    tools=None
):

    request = {

        "model":
            "deepseek-v4-flash",

        "messages":
            messages,

        "temperature":
            0.3

    }


    if tools:

        request["tools"] = tools

        request["tool_choice"] = "auto"


    response = client.chat.completions.create(
        **request
    )


    return response
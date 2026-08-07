#负责：和模型通信
#输入:prompt文本;输出:模型回复
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key = os.getenv("DEEPSEEK_API_KEY"),
    base_url = "https://api.deepseek.com"
)

def ask_llm(prompt):

    resp = client.chat.completions.create(

        model = "deepseek-chat",

        messages = [
            {
                "role": "user",
                "content": prompt,
            }
        ],

        temperature=0.7

    )

    return resp.choices[0].message.content
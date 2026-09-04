# api/app.py

from fastapi import FastAPI
from pydantic import BaseModel

from src.agent.agent import run_agent


# =========================================================
# FastAPI 应用
# =========================================================

app = FastAPI(
    title="AI News Agent",
    description="AI 新闻智能 Agent API",
    version="1.0.0"
)


# =========================================================
# 请求模型
# =========================================================

class AskRequest(BaseModel):

    question: str


# =========================================================
# 响应模型
# =========================================================

class AskResponse(BaseModel):

    answer: str


# =========================================================
# 根路径
# =========================================================

@app.get("/")
def root():

    return {
        "message": "AI News Agent API is running"
    }


# =========================================================
# 健康检查
# =========================================================

@app.get("/health")
def health():

    return {
        "status": "ok"
    }


# =========================================================
# Agent 问答
# =========================================================

@app.post(
    "/ask",
    response_model=AskResponse
)
def ask(request: AskRequest):

    question = request.question.strip()

    if not question:

        return AskResponse(
            answer="问题不能为空。"
        )

    answer = run_agent(
        question
    )

    return AskResponse(
        answer=answer
    )
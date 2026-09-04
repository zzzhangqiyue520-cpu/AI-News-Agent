# AI-News-Agent

一个基于 Python 构建的 AI 新闻采集、知识库、RAG 与智能 Agent 项目。

项目从新闻数据采集开始，逐步构建：

**新闻采集 → 正文解析 → 去重 → LLM 分析 → SQLite → Chunking → Embedding → Chroma → Hybrid Retrieval → Tool Calling → Agent → FastAPI**

项目主要用于实践完整的 AI Agent 工程链路，包括数据获取、数据处理、数据库、向量数据库、RAG、Tool Calling、Agent 和 API 服务。

---

## 1. 项目简介

AI-News-Agent 是一个面向 AI 科技新闻的个人 AI Agent 项目。

系统会从多个 AI 新闻来源获取新闻，对新闻进行解析和结构化处理，然后使用 LLM 对新闻进行：

- 摘要
- 关键词提取
- 新闻分类

处理后的新闻长期保存到 SQLite 数据库。

同时，系统会将新闻正文切分成多个 Chunk，通过 Embedding 模型转换为向量，并保存到 Chroma 向量数据库。

在此基础上，Agent 可以根据用户问题自动选择：

- 最新新闻查询
- 分类新闻查询
- 新闻来源查询
- 关键词搜索
- Vector Retrieval
- Hybrid Retrieval
- 新闻详情查询

最终生成中文回答。

用户不需要了解 SQLite、Chroma 或检索系统，只需要直接提出自然语言问题。

例如：

```text
最近有哪些 AI 新闻？

最近有哪些机器人新闻？

Gemini 最近有哪些新闻？

Anthropic 最近有什么新闻？

为什么 Gemini Robotics 2 的全身控制很重要？

Gemini Robotics 2 和 Gemini Robotics ER 2 有什么区别？

比较一下 DeepMind 和 Anthropic 最近的大模型新闻。
```

---

# 2. 项目整体架构

```text
                         AI-News-Agent
                                |
              +-----------------+------------------+
              |                                    |
              ↓                                    ↓
           新闻采集层                           Agent 层
              |                                    |
       +------+------+                             ↓
       |             |                            LLM
       ↓             ↓                             |
    DeepMind      Anthropic                        |
       |             |                             |
       +------+------+                             |
              ↓                                    |
           统一数据                                |
              ↓                                    |
           正文解析                                |
              ↓                                    |
             去重                                  |
              ↓                                    |
          LLM 新闻分析                             |
              ↓                                    |
           SQLite <-------------------------------+
              |
              ↓
        Incremental Indexer
              |
              ↓
           Chunking
              |
              ↓
           Embedding
              |
              ↓
            Chroma
              |
       +------+----------------+
       |                       |
       ↓                       ↓
Vector Retrieval       Keyword Retrieval
       |                       |
    Chroma                   SQLite
       |                       |
       +----------+------------+
                  ↓
          Hybrid Retrieval
                  ↓
               Top-K
                  ↓
               Context
                  ↓
                Agent
                  ↓
                 LLM
                  ↓
               Answer
                  ↓
              FastAPI
                  ↓
               Client
```

---

# 3. 多来源新闻采集

目前已经接入：

- Google DeepMind
- Anthropic

不同来源使用不同的数据获取方式。

## DeepMind

主要流程：

```text
DeepMind 新闻列表
        ↓
HTML 解析
        ↓
获取文章 URL
        ↓
请求详情页
        ↓
正文提取
        ↓
统一新闻结构
```

## Anthropic

目前通过 RSS 获取：

```text
Anthropic RSS
      ↓
XML
      ↓
RSS Parser
      ↓
结构化新闻
```

最终两个来源都会转换为统一的数据结构，交给后续去重、AI 分析和数据库处理。

---

# 4. 新闻数据结构

最终保存的数据包含：

```json
{
    "title": "Gemini Robotics 2 brings whole body intelligence to robots",
    "url": "https://deepmind.google/blog/...",
    "time": "July 2026",
    "content": "完整新闻正文...",
    "source": "DeepMind",
    "analysis": {
        "summary": "新闻摘要",
        "keywords": [
            "Gemini Robotics 2",
            "全身控制",
            "机器人"
        ],
        "category": "机器人"
    },
    "id": "294161fcfd13af805c2ecc1d2543ebd0"
}
```

---

# 5. 新闻去重

系统根据新闻 URL 生成唯一 ID：

```text
新闻 URL
   ↓
Hash
   ↓
新闻唯一 ID
```

SQLite 同时对 `hash` 和 `url` 设置唯一约束。

去重包括：

1. 当前抓取批次内去重
2. SQLite 历史新闻去重

例如：

```text
第一次运行：
新增 30 条

第二次运行：
新增 0 条
重复 30 条
```

因此重复运行程序不会不断生成重复新闻。

---

# 6. LLM 新闻分析

系统使用 DeepSeek API 对新新闻进行分析。

分析内容包括：

```text
摘要
关键词
分类
```

返回结构：

```json
{
    "summary": "新闻摘要",
    "keywords": [
        "Gemini Robotics 2",
        "全身控制",
        "多机器人协作"
    ],
    "category": "机器人"
}
```

目前支持以下分类：

```text
AI技术
机器人
大模型
开源
科研
企业动态
其他
```

LLM 调用之后，会从 `ChatCompletion` 中获取真正的文本内容，再进行 JSON 解析。

同时会对返回结构进行基本校验。

如果 LLM 请求或 JSON 解析出现异常，则使用默认结果进行兜底，避免单条新闻导致整个采集流程停止。

---

# 7. SQLite 新闻数据库

SQLite 数据库保存位置：

```text
data/news.db
```

主要字段：

```text
id
hash
title
url
source
content
summary
category
created_at
```

主要数据库功能：

```python
create_table()

save_news()

exists_news()

get_news()

get_latest_news()

get_news_by_source()

get_news_by_category()

search_news()

get_news_detail()

count_news()
```

SQLite 作为系统的主要结构化数据存储。

---

# 8. Chunking

长新闻不会直接作为一个整体进行向量化，而是先切分成多个 Chunk。

当前默认参数：

```text
chunk_size = 1000
overlap = 200
```

例如：

```text
Chunk 1
0 ~ 1000

Chunk 2
800 ~ 1800

Chunk 3
1600 ~ 2600
```

相邻 Chunk 保留 200 个字符的重叠区域，用于降低重要信息恰好出现在边界位置所造成的信息损失。

核心流程：

```text
完整新闻正文
      ↓
split_text()
      ↓
多个 Chunk
```

---

# 9. Embedding

当前使用的 Embedding 模型：

```text
paraphrase-multilingual-MiniLM-L12-v2
```

新闻 Chunk 的向量化流程：

```text
新闻 Chunk
    ↓
Embedding Model
    ↓
Vector
    ↓
Chroma
```

用户查询也使用相同模型：

```text
用户问题
    ↓
Embedding Model
    ↓
Query Vector
```

然后与 Chroma 中保存的新闻向量进行语义相似度检索。

---

# 10. Chroma 向量数据库

Chroma 数据保存位置：

```text
data/chroma/
```

主要保存：

- 新闻 Chunk
- Embedding Vector
- Metadata

Metadata 主要包括：

```text
news_id
title
url
source
category
chunk_index
```

SQLite 和 Chroma 承担不同职责。

## SQLite

负责：

```text
结构化新闻
完整正文
摘要
分类
来源
```

## Chroma

负责：

```text
Chunk
Embedding
语义检索
Metadata
```

两者互相配合，而不是相互替代。

---

# 11. Vector Retrieval

Vector Retrieval 用于进行语义搜索。

流程：

```text
用户问题
   ↓
Embedding
   ↓
Query Vector
   ↓
Chroma
   ↓
相关新闻 Chunk
```

例如：

```text
机器人如何实现全身控制？
```

即使新闻中不存在完全相同的句子，也可以通过语义相似度找到相关内容。

---

# 12. Keyword Retrieval

除了向量检索之外，系统保留传统的 SQLite 关键词检索。

流程：

```text
用户问题
   ↓
关键词提取
   ↓
SQLite
   ↓
关键词匹配
```

关键词会用于搜索新闻的：

```text
title
summary
category
```

系统会根据命中的关键词计算 Keyword Score。

---

# 13. Hybrid Retrieval

为了同时利用语义检索和关键词检索，项目实现了 Hybrid Retrieval。

整体流程：

```text
                     用户问题
                         |
                +--------+--------+
                |                 |
                ↓                 ↓
        Vector Retrieval   Keyword Retrieval
                |                 |
                ↓                 ↓
             Chroma             SQLite
                |                 |
                +--------+--------+
                         ↓
                       合并
                         ↓
                       去重
                         ↓
                   Hybrid Score
                         ↓
                       Top-K
```

当前 Hybrid Score：

```python
hybrid_score = (
    0.6 * vector_score
    + 0.3 * keyword_score
    + 0.1 * metadata_score
)
```

其中：

```text
Vector Score
→ 语义相似度

Keyword Score
→ 查询关键词命中程度

Metadata Score
→ category / source 匹配程度
```

这样可以同时利用语义信息、关键词匹配和用户指定的元数据范围。

---

# 14. Metadata Filter

RAG 支持根据新闻 Metadata 缩小检索范围。

目前支持：

```text
category
source
```

例如：

```text
Anthropic 最近有哪些大模型进展？
```

可以指定：

```text
source = Anthropic
category = 大模型
```

然后进行：

```text
Metadata Filter
      ↓
Vector Retrieval
      +
Keyword Retrieval
      ↓
Hybrid Retrieval
```

如果同时设置多个过滤条件，则使用逻辑 AND 进行组合。

---

# 15. 增量向量索引

项目已经实现 Incremental Vector Indexing。

传统方式：

```text
SQLite
 ↓
全部新闻
 ↓
全部重新 Chunk
 ↓
全部重新 Embedding
 ↓
全部写入 Chroma
```

当前项目：

```text
SQLite
 ↓
检查 Chroma 中已有 news_id
 ↓
找出尚未索引的新闻
 ↓
只处理新增新闻
 ↓
Chunk
 ↓
Embedding
 ↓
Chroma.add()
```

例如：

```text
SQLite = 35 条
Chroma = 已索引 35 条
```

增加 2 条新闻：

```text
SQLite = 37 条
        ↓
发现 2 条新增新闻
        ↓
只处理这 2 条新闻
        ↓
生成 Chunk
        ↓
Embedding
        ↓
写入 Chroma
```

再次执行：

```text
SQLite = 37
Chroma = 已索引 37 条
```

则：

```text
新增新闻 = 0
```

不会重新 Embedding 已经存在的新闻。

---

# 16. 自动向量索引

增量索引已经集成到主程序。

运行：

```bash
python main.py
```

会自动执行：

```text
新闻采集
    ↓
去重
    ↓
AI 分析
    ↓
SQLite
    ↓
自动调用 build_index()
    ↓
增量更新 Chroma
```

因此正常情况下不需要再手动执行向量索引。

同时仍然可以单独执行：

```bash
python -m src.rag.indexer
```

用于检查或手动维护向量库。

---

# 17. Agent

Agent 使用 LLM Tool Calling 能力，根据用户问题自主选择工具。

目前提供：

```text
search_latest_news
search_category_news
search_source_news
search_keyword
search_knowledge
get_news_detail
```

---

## 17.1 查询最新新闻

用户：

```text
最近有哪些 AI 新闻？
```

Agent 可以选择：

```text
search_latest_news
```

---

## 17.2 查询分类

用户：

```text
最近有哪些机器人新闻？
```

Agent 可以选择：

```text
search_category_news
```

参数：

```json
{
    "category": "机器人"
}
```

---

## 17.3 查询新闻来源

用户：

```text
Anthropic 最近有什么新闻？
```

Agent 可以选择：

```text
search_source_news
```

---

## 17.4 关键词查询

用户：

```text
Gemini 最近有哪些新闻？
```

Agent 可以选择：

```text
search_keyword
```

---

## 17.5 知识库检索

用户：

```text
为什么 Gemini Robotics 2 的全身控制很重要？
```

Agent 可以调用：

```text
search_knowledge
```

内部执行：

```text
Hybrid Retrieval
    ↓
SQLite + Chroma
    ↓
相关知识
```

---

## 17.6 新闻详情

用户：

```text
Gemini Robotics 2 具体讲了什么？
```

Agent 可以：

```text
搜索新闻
    ↓
获得 news_id
    ↓
get_news_detail()
    ↓
读取完整正文
```

---

# 18. Multi-Step Agent

Agent 支持多轮 Tool Calling。

例如：

```text
用户问题
   ↓
LLM
   ↓
search_keyword
   ↓
找到候选新闻
   ↓
LLM 再次判断
   ↓
get_news_detail
   ↓
读取完整正文
   ↓
LLM
   ↓
最终回答
```

对于比较问题，也可以进行多步检索。

例如：

```text
比较 Gemini Robotics 2 和 Gemini Robotics ER 2
```

可以：

```text
搜索对象 A
    ↓
搜索对象 B
    ↓
必要时读取正文
    ↓
LLM 综合比较
    ↓
最终回答
```

Agent 当前限制：

```python
MAX_TOOL_ROUNDS = 5
```

用于防止异常情况下无限调用工具。

---

# 19. Agent + RAG

Agent 和 RAG 已经完成集成。

完整流程：

```text
用户问题
    ↓
Agent
    ↓
LLM 判断是否需要知识库
    ↓
search_knowledge
    ↓
Hybrid Retrieval
    ↓
SQLite + Chroma
    ↓
相关 Chunk
    ↓
Agent
    ↓
LLM
    ↓
最终回答
```

例如：

```text
为什么 Gemini Robotics 2 的全身控制很重要？
```

Agent 可以自动选择：

```text
search_knowledge
```

然后根据知识库返回的内容生成回答。

---

# 20. FastAPI

项目已经通过 FastAPI 提供 HTTP API。

启动：

```bash
uvicorn api.app:app --reload
```

默认地址：

```text
http://127.0.0.1:8000
```

Swagger 文档：

```text
http://127.0.0.1:8000/docs
```

---

## 20.1 根路径

```http
GET /
```

返回：

```json
{
    "message": "AI News Agent API is running"
}
```

---

## 20.2 健康检查

```http
GET /health
```

返回：

```json
{
    "status": "ok"
}
```

---

## 20.3 Agent 问答

```http
POST /ask
```

请求：

```json
{
    "question": "为什么 Gemini Robotics 2 重要？"
}
```

返回：

```json
{
    "answer": "..."
}
```

FastAPI 的作用是将现有 Agent 能力通过 HTTP 暴露出来，使网页、App 或其他程序可以调用 Agent。

---

# 21. 异常处理与稳定性

项目加入了多层异常处理。

## 网络请求

支持：

```text
Timeout
HTTP 错误
ClientError
请求重试
```

避免因为单次网络故障导致整个任务终止。

---

## DeepMind

列表请求：

```text
请求失败
   ↓
重试
   ↓
仍失败
   ↓
跳过本次列表
```

文章请求：

```text
请求失败
   ↓
重试
   ↓
仍失败
   ↓
跳过该文章
```

单篇文章失败不会影响其他文章。

---

## Anthropic

RSS 请求：

```text
请求失败
   ↓
重试
   ↓
仍失败
   ↓
返回空列表
```

不会影响其他新闻源。

---

## LLM

LLM 返回：

```text
ChatCompletion
```

之后：

```text
ChatCompletion
    ↓
message.content
    ↓
JSON 清理
    ↓
json.loads()
```

如果 JSON 解析失败，则使用默认结果：

```json
{
    "summary": "",
    "keywords": [],
    "category": "其他"
}
```

避免单条新闻导致整个任务停止。

---

## SQLite

SQLite 连接设置了 timeout。

针对：

```text
database is locked
```

支持有限次数重试。

---

## Chroma

SQLite 是主要数据源，Chroma 是派生向量索引。

如果 Chroma 更新失败：

```text
SQLite 数据仍然保留
        ↓
下一次执行增量索引
        ↓
检测缺失 news_id
        ↓
补建 Chroma
```

这样可以避免因为向量库暂时失败而导致结构化新闻数据丢失。

---

# 22. 日志系统

日志保存位置：

```text
logs/app.log
```

主要记录：

```text
程序启动
新闻源状态
抓取结果
去重结果
LLM 调用
Agent 工具选择
工具参数
工具执行
异常信息
```

例如：

```text
用户问题
Agent第 1 轮思考
模型选择工具
工具参数
工具执行完成
Agent决定直接回答
```

---

# 23. 项目结构

```text
AI-News-Agent/
│
├── api/
│   ├── __init__.py
│   └── app.py
│
├── src/
│   ├── __init__.py
│   │
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── tools.py
│   │   └── tool_schema.py
│   │
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── analyzer.py
│   │   └── llm_client.py
│   │
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── chunker.py
│   │   ├── indexer.py
│   │   └── retriever.py
│   │
│   ├── sources/
│   │   ├── base.py
│   │   │
│   │   ├── deepmind/
│   │   │   ├── crawler.py
│   │   │   ├── detail.py
│   │   │   └── source.py
│   │   │
│   │   └── anthropic/
│   │       ├── crawler.py
│   │       ├── parser.py
│   │       └── source.py
│   │
│   ├── config.py
│   ├── database.py
│   ├── logger.py
│   └── utils.py
│
├── data/
│
├── logs/
│
├── main.py
├── main_agent.py
├── requirements.txt
├── .gitignore
└── README.md
```

运行时可能存在：

```text
data/news.db
data/chroma/
logs/app.log
```

这些属于本地生成的数据，不需要提交到 Git。

---

# 24. 技术栈

## 编程语言

```text
Python
```

## 异步与数据采集

```text
asyncio
aiohttp
BeautifulSoup
RSS
```

## 数据库

```text
SQLite
```

## 大模型

```text
DeepSeek API
OpenAI-compatible SDK
```

## Embedding

```text
Sentence Transformers
paraphrase-multilingual-MiniLM-L12-v2
```

## 向量数据库

```text
Chroma
```

## Agent

```text
LLM Tool Calling
```

## API

```text
FastAPI
Uvicorn
```

---

# 25. 安装

创建虚拟环境：

```bash
python -m venv .venv
```

Windows 激活：

```bash
.venv\Scripts\activate
```

安装依赖：

```bash
pip install -r requirements.txt
```

---

# 26. 环境变量

项目使用 `.env` 保存 API Key。

创建：

```text
.env
```

配置：

```env
DEEPSEEK_API_KEY=你的API_KEY
```

不要将 `.env` 提交到 GitHub。

---

# 27. 运行新闻采集

运行：

```bash
python main.py
```

系统会自动执行：

```text
获取新闻
    ↓
解析
    ↓
正文提取
    ↓
URL Hash 去重
    ↓
LLM 分析
    ↓
SQLite 保存
    ↓
增量更新 Chroma
```

---

# 28. 手动维护向量库

虽然 `main.py` 已经会自动进行增量索引，但也可以单独执行：

```bash
python -m src.rag.indexer
```

程序会自动检查：

```text
SQLite 中有哪些新闻
        ↓
Chroma 中已经有哪些 news_id
        ↓
找出尚未索引的数据
        ↓
只处理这些数据
```

---

# 29. 运行 Agent

运行：

```bash
python main_agent.py
```

然后输入自然语言问题。

例如：

```text
最近有哪些 AI 新闻？
```

```text
最近有哪些机器人新闻？
```

```text
Gemini 最近有哪些新闻？
```

```text
为什么 Gemini Robotics 2 的全身控制很重要？
```

```text
Gemini Robotics 2 具体讲了什么？
```

```text
比较 Gemini Robotics 2 和 Gemini Robotics ER 2。
```

---

# 30. 启动 API

运行：

```bash
uvicorn api.app:app --reload
```

打开：

```text
http://127.0.0.1:8000/docs
```

即可通过 Swagger 测试 Agent API。

---

# 31. Git 管理

以下内容属于本地运行数据，不建议提交：

```gitignore
.venv/
__pycache__/
*.pyc

.idea/

.env

logs/

data/*.html
data/news.json
data/news.db
data/chroma/
```

建议提交：

```text
api/
src/
main.py
main_agent.py
requirements.txt
README.md
.gitignore
```

---

# 32. 当前项目状态

当前已经完成：

```text
✅ Python 项目结构

✅ 多来源新闻采集

✅ DeepMind HTML 抓取

✅ Anthropic RSS 抓取

✅ 新闻正文提取

✅ URL Hash 去重

✅ SQLite 新闻数据库

✅ LLM 新闻摘要

✅ LLM 关键词提取

✅ LLM 新闻分类

✅ Chunking

✅ Embedding

✅ Chroma 向量数据库

✅ Vector Retrieval

✅ Keyword Retrieval

✅ Hybrid Retrieval

✅ Metadata Filter

✅ Agent Tool Calling

✅ Multi-Step Agent

✅ Agent + RAG

✅ Incremental Vector Indexing

✅ 新闻采集与向量库自动同步

✅ 网络异常重试

✅ LLM 异常处理

✅ SQLite 锁重试

✅ 日志系统

✅ FastAPI

✅ Swagger API
```

---

# 33. 项目定位

AI-News-Agent 不是一个单纯的新闻爬虫，也不是一个简单的 LLM Chatbot。

它是一个综合性的 AI 工程实践项目，将：

```text
数据采集
+
数据处理
+
数据库
+
LLM
+
Embedding
+
向量数据库
+
RAG
+
Tool Calling
+
Agent
+
API
```

连接成一个完整系统。

项目重点不是使用复杂 Agent 框架，而是自己理解并实现：

```text
数据
 ↓
知识库
 ↓
检索
 ↓
LLM
 ↓
Agent
 ↓
API
```

这一整套完整链路。

---

# 34. Version

当前版本：

```text
AI-News-Agent v1.0
```

v1.0 已完成：

```text
稳定新闻采集
+
历史新闻保存
+
AI 新闻分析
+
自动增量向量索引
+
Hybrid Retrieval
+
Metadata Filter
+
Agent
+
RAG
+
Tool Calling
+
FastAPI
```

---

# 35. 后续优化方向

v1.0 已经完成核心功能。

后续重点放在质量和工程化，而不是继续无限增加功能。

可以进一步优化：

```text
1. 增加更多高质量新闻来源

2. 优化 RAG 检索效果

3. 优化 Agent 工具选择

4. 增加更完善的自动化测试

5. 增加前端界面

6. 部署到服务器

7. 增加监控与性能优化
```

这些属于 v1.0 之后的扩展方向，不影响当前版本的完整性。

---

# 36. License

本项目主要用于个人学习、AI Agent 工程实践和技术研究。

如需正式开源发布，可根据实际情况补充具体 License。
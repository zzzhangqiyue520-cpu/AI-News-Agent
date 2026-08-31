# AI-News-Agent

一个基于 Python 的 AI 新闻采集、知识库构建与智能问答 Agent 项目。

项目从新闻采集开始，逐步构建：

**新闻采集 → 正文解析 → 去重 → AI 分析 → SQLite → Embedding → Chroma → Hybrid Retrieval → Tool Calling → Agent → RAG**

目前已经完成基础的新闻知识库、向量检索、RAG 和多步 Agent 能力。

---

## 1. 项目简介

AI-News-Agent 是一个面向 AI 科技新闻的个人 AI Agent 项目。

系统会从多个 AI 新闻来源获取新闻，对新闻进行解析和结构化处理，然后使用 LLM 对新闻进行：

- 摘要
- 关键词提取
- 新闻分类

处理后的新闻会长期保存到 SQLite 数据库中。

同时，系统会对新闻正文进行 Chunking 和 Embedding，并将向量保存到 Chroma 向量数据库，使 Agent 可以通过自然语言检索历史新闻。

用户无需了解数据库结构，只需要直接向 Agent 提问。

例如：

```text
最近有哪些 AI 新闻？

最近有哪些机器人新闻？

Gemini 最近有哪些新闻？

Anthropic 最近有什么新闻？

Gemini Robotics 2 有什么意义？

为什么 Gemini Robotics 2 的全身控制很重要？

Gemini Robotics 2 和 Gemini Robotics ER 2 有什么区别？

比较一下 DeepMind 和 Anthropic 最近的大模型新闻。
```

---

# 2. 项目整体架构

```text
                         AI-News-Agent
                              |
             +----------------+----------------+
             |                                 |
             ↓                                 ↓
          新闻采集层                         Agent 层
             |                                 |
       +-----+------+                          ↓
       |            |                         LLM
       ↓            ↓                          |
   DeepMind     Anthropic                      |
       |            |                          |
       +-----+------+                          |
             ↓                                 |
          Parser                               |
             ↓                                 |
          正文提取                              |
             ↓                                 |
            去重                                |
             ↓                                 |
         AI 新闻分析                            |
             ↓                                 |
          SQLite <-----------------------------+
             |
             +-------------------+
             |                   |
             ↓                   ↓
         原始新闻数据          RAG 索引
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
                         +-------+-------+
                         |               |
                         ↓               ↓
                    Vector Search   Keyword Search
                         |               |
                         ↓               ↓
                      Chroma          SQLite
                         \               /
                          \             /
                           ↓           ↓
                         Hybrid Retrieval
                                |
                                ↓
                            Top-K Chunks
                                |
                                ↓
                              Context
                                |
                                ↓
                               LLM
                                |
                                ↓
                              回答
```

---

# 3. 核心功能

## 3.1 多来源新闻采集

目前已经接入：

- Google DeepMind
- Anthropic

后续可以继续增加其他稳定来源。

不同来源统一转换成统一的新闻数据结构。

---

## 3.2 新闻正文解析

新闻列表中的文章会进一步获取完整正文。

最终新闻数据结构类似：

```json
{
    "title": "Gemini Robotics 2 brings whole body intelligence to robots",
    "url": "https://deepmind.google/blog/gemini-robotics-2-brings-whole-body-intelligence-to-robots/",
    "time": "July 2026",
    "content": "完整新闻正文...",
    "source": "DeepMind",
    "analysis": {
        "summary": "谷歌发布Gemini Robotics 2，赋予机器人全身智能控制、精细操作与多机协作能力。",
        "keywords": [
            "Gemini Robotics 2",
            "全身控制",
            "多机器人协作"
        ],
        "category": "机器人"
    },
    "id": "294161fcfd13af805c2ecc1d2543ebd0"
}
```

---

## 3.3 新闻去重

使用新闻 URL 生成 Hash：

```text
新闻 URL
    ↓
MD5
    ↓
新闻唯一 ID
```

同时 SQLite 对 Hash 和 URL 设置唯一约束。

因此重复运行程序时，同一篇新闻不会重复保存。

例如：

```text
第一次运行：
新增 30 条

第二次运行：
新增 0 条
重复 30 条
```

---

# 4. AI 新闻分析

使用 LLM 对新新闻进行自动分析。

分析结果包括：

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

目前支持的分类：

```text
AI技术
机器人
大模型
开源
科研
企业动态
其他
```

---

# 5. SQLite 新闻数据库

新闻长期保存到：

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

数据库主要提供：

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

因此历史新闻不会因为每天重新运行程序而消失。

---

# 6. Vector RAG

项目使用 Embedding 模型将新闻文本转换成向量，并使用 Chroma 保存这些向量。

核心流程：

```text
新闻正文
    ↓
Chunking
    ↓
Embedding
    ↓
Chroma
```

Chroma 数据保存位置：

```text
data/chroma/
```

---

# 7. Chunking

为了提高检索精度，不直接将一篇完整新闻只保存成一个向量。

当前采用：

```text
完整新闻
    ↓
多个 Chunk
    ↓
每个 Chunk 独立 Embedding
```

例如：

```text
Gemini Robotics 2

Chunk 0
模型总体介绍

Chunk 1
全身控制

Chunk 2
精细操作

Chunk 3
多机器人协作

Chunk 4
On-Device

Chunk 5
安全机制
```

每个 Chunk 都会记录对应的新闻信息。

例如：

```json
{
    "news_id": 62,
    "title": "Gemini Robotics 2",
    "source": "DeepMind",
    "category": "机器人",
    "chunk_index": 3
}
```

这样可以知道检索出来的文本块属于哪一篇新闻。

---

# 8. Embedding

目前使用：

```text
paraphrase-multilingual-MiniLM-L12-v2
```

Embedding 的基本过程：

```text
新闻 Chunk
    ↓
Embedding Model
    ↓
向量
```

用户查询也会经过相同的 Embedding 模型转换为向量：

```text
用户问题
    ↓
Embedding Model
    ↓
Query Vector
```

然后与 Chroma 中已有的新闻向量进行相似度搜索。

---

# 9. Chroma 向量数据库

Chroma 用于保存：

- 新闻 Chunk
- Embedding Vector
- 新闻 Metadata

结构大致为：

```text
SQLite
    └── 原始结构化新闻

Chroma
    ├── Embedding
    ├── Chunk
    └── Metadata
```

SQLite 和 Chroma 并不是互相替代，而是承担不同职责。

SQLite：

```text
保存完整结构化新闻
```

Chroma：

```text
负责语义向量检索
```

---

# 10. Vector Retrieval

用户问题首先转换为向量：

```text
用户问题
    ↓
Embedding
    ↓
Query Vector
    ↓
Chroma
    ↓
最相关的新闻 Chunk
```

例如：

```text
机器人如何实现全身控制？
```

即使新闻中没有完全相同的句子，也可以通过语义相似度找到：

```text
Gemini Robotics 2
Gemini Robotics ER 2
```

---

# 11. Keyword Retrieval

除了向量检索之外，系统还保留传统的 SQLite 关键词检索。

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

例如：

```text
Gemini Robotics 最近有什么进展？
```

可能提取：

```text
Gemini
Robotics
```

然后分别进行关键词搜索。

---

# 12. Hybrid Retrieval

为了结合关键词检索和语义检索的优点，系统实现了 Hybrid Retrieval。

整体流程：

```text
                    用户问题
                       |
               +-------+-------+
               |               |
               ↓               ↓
         Vector Retrieval  Keyword Retrieval
               |               |
               ↓               ↓
             Chroma          SQLite
               |               |
               +-------+-------+
                       |
                       ↓
                     合并
                       |
                       ↓
                      去重
                       |
                       ↓
                  Hybrid Score
                       |
                       ↓
                     Top-K
```

当前版本采用：

```python
hybrid_score = (
    0.7 * vector_score
    + 0.3 * keyword_score
)
```

这个评分方式主要用于项目学习和验证。

---

# 13. Agent

Agent 使用 LLM 的 Tool Calling 能力，根据用户问题自主选择工具。

目前主要工具包括：

```text
search_latest_news
search_category_news
search_source_news
search_keyword
search_knowledge
get_news_detail
```

---

## 13.1 查询最新新闻

用户：

```text
最近有哪些 AI 新闻？
```

Agent 可以选择：

```text
search_latest_news
```

---

## 13.2 查询分类

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

## 13.3 查询来源

用户：

```text
Anthropic 最近有什么新闻？
```

Agent 可以选择：

```text
search_source_news
```

---

## 13.4 关键词查询

用户：

```text
Gemini 最近有哪些新闻？
```

Agent 可以选择：

```text
search_keyword
```

---

## 13.5 知识库检索

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

## 13.6 新闻详情

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

# 14. Multi-Step Agent

Agent 不局限于只调用一次工具。

例如：

```text
用户问题
    ↓
LLM
    ↓
search_keyword
    ↓
获得候选新闻
    ↓
LLM再次判断
    ↓
get_news_detail
    ↓
读取完整正文
    ↓
LLM继续判断
    ↓
最终回答
```

也可以：

```text
用户：
比较 Gemini Robotics 2 和 Gemini Robotics ER 2。

    ↓

搜索新闻 A
    ↓
搜索新闻 B
    ↓
读取 A 正文
    ↓
读取 B 正文
    ↓
LLM 比较
    ↓
最终回答
```

因此项目已经具备基础的多步 Tool Calling 能力。

---

# 15. Agent + RAG

目前已经将 Agent 和 RAG 连接起来。

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
返回 Agent
    ↓
LLM 分析
    ↓
最终回答
```

例如：

```text
为什么 Gemini Robotics 2 的全身控制很重要？
```

可能执行：

```text
search_knowledge
        ↓
找到相关 Chunk
        ↓
必要时读取新闻详情
        ↓
LLM 分析
        ↓
最终回答
```

---

# 16. 日志系统

日志保存位置：

```text
logs/app.log
```

记录内容包括：

```text
用户问题
模型选择的工具
工具参数
工具执行结果
Agent 思考轮次
异常信息
最终回答生成
```

例如：

```text
用户问题: Gemini Robotics 2 有什么意义？
Agent第 1 轮思考
模型选择工具: search_knowledge
工具参数: ...
工具执行完成: search_knowledge
Agent第 2 轮思考
模型选择工具: get_news_detail
工具参数: ...
工具执行完成: get_news_detail
Agent决定直接回答
```

---

# 17. 项目结构

```text
AI-News-Agent/
│
├── data/
│   ├── news.db
│   ├── news.json
│   └── chroma/
│
├── logs/
│   └── app.log
│
├── src/
│   │
│   ├── agent/
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
│   │   ├── deepmind/
│   │   └── anthropic/
│   │
│   ├── config.py
│   ├── database.py
│   ├── logger.py
│   ├── news_manager.py
│   └── utils.py
│
├── main.py
├── main_agent.py
├── test_database.py
├── test_agent_tool.py
├── test_vector_rag.py
├── test_hybrid_rag.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

---

# 18. 技术栈

## 编程语言

```text
Python
```

## 数据采集

```text
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
```

## Embedding

```text
Sentence Transformers
```

## 向量数据库

```text
Chroma
```

## Agent

```text
OpenAI-compatible Tool Calling
```

---

# 19. 安装

创建虚拟环境：

```bash
python -m venv .venv
```

激活虚拟环境：

Windows：

```bash
.venv\Scripts\activate
```

安装依赖：

```bash
pip install -r requirements.txt
```

---

# 20. 环境变量

在项目根目录创建：

```text
.env
```

配置：

```env
DEEPSEEK_API_KEY=你的API_KEY
```

不要将 `.env` 提交到 GitHub。

---

# 21. 运行新闻采集

运行：

```bash
python main.py
```

系统会：

```text
获取新闻
    ↓
解析新闻
    ↓
正文提取
    ↓
Hash 去重
    ↓
AI 分析
    ↓
SQLite 保存
```

---

# 22. 构建向量库

首次构建 Chroma：

```bash
python src/rag/indexer.py
```

过程：

```text
SQLite 新闻
    ↓
Chunking
    ↓
Embedding
    ↓
Chroma
```

---

# 23. 测试向量检索

运行：

```bash
python test_vector_rag.py
```

用于测试：

```text
Embedding
    ↓
Chroma
    ↓
Vector Retrieval
```

例如：

```text
机器人如何实现全身控制？
```

---

# 24. 测试 Hybrid Retrieval

运行：

```bash
python test_hybrid_rag.py
```

用于测试：

```text
Keyword Retrieval
+
Vector Retrieval
↓
Hybrid Retrieval
```

---

# 25. 运行 Agent

运行：

```bash
python main_agent.py
```

然后直接输入自然语言问题。

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

# 26. Git 管理

以下内容属于本地生成文件，不建议提交到 Git：

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
src/
main.py
main_agent.py
requirements.txt
README.md
.gitignore
```

---

# 27. 当前项目状态

已经完成：

```text
✅ Python 项目结构

✅ 多来源新闻采集

✅ HTML / RSS 数据获取

✅ 新闻正文提取

✅ Hash 新闻去重

✅ SQLite 历史新闻库

✅ AI 新闻摘要

✅ AI 分类

✅ 关键词提取

✅ Embedding

✅ Chroma 向量数据库

✅ Chunking

✅ Vector Retrieval

✅ Keyword Retrieval

✅ Hybrid Retrieval

✅ Agent Tool Calling

✅ Multi-Step Agent

✅ Agent + RAG

✅ 日志系统
```

---

# 28. 后续完善计划

项目目前已经具备完整的基础 Agent + RAG 链路。

后续重点不再是无限增加功能，而是提高系统的完整度和稳定性。

计划包括：

```text
1. 优化 Agent 工具选择

2. 优化 RAG 检索质量

3. Chroma 增量更新

4. 新闻采集与向量库自动同步

5. 增强异常处理与容错

6. 增加 FastAPI 接口

7. 完整回归测试

8. 项目最终封版
```

---

# 29. 项目最终目标

最终希望形成：

```text
                      新闻来源
                         ↓
                      自动采集
                         ↓
                       解析
                         ↓
                       去重
                         ↓
                    AI 新闻分析
                         ↓
                      SQLite
                         ↓
                     Chunking
                         ↓
                    Embedding
                         ↓
                      Chroma
                         ↓
                 Hybrid Retrieval
                         ↓
                       Agent
                         ↓
                   Tool Calling
                         ↓
                        LLM
                         ↓
                  总结 / 比较 / 分析
                         ↓
                       用户
```

---

# 30. 项目学习目标

这个项目主要用于实践以下 AI 工程技术：

```text
Web Data Collection
        +
Data Processing
        +
SQLite
        +
LLM
        +
Embedding
        +
Vector Database
        +
RAG
        +
Tool Calling
        +
Agent
```

通过一个完整项目，学习从：

```text
数据获取
```

到：

```text
知识库构建
```

再到：

```text
智能 Agent 应用
```

的完整工程流程。

---

# 31. 项目定位

AI-News-Agent 不是一个单纯的新闻爬虫，也不是一个简单的 LLM Chatbot。

它更适合作为一个：

> **AI Agent + RAG + 数据采集 + 数据库 + LLM 的综合工程实践项目。**

项目重点不在于追求复杂的 Agent 框架，而在于理解并实现：

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
```

这一整套链路。

---

# 32. Version

Current Version:

```text
AI-News-Agent v0.x
```

目标版本：

```text
AI-News-Agent v1.0
```

v1.0 的目标是：

```text
稳定新闻采集
+
历史新闻保存
+
自动向量索引
+
Hybrid Retrieval
+
Agent
+
RAG
+
API
```

---

# 33. License

本项目主要用于个人学习、AI Agent 工程实践和技术研究。

具体开源协议将在项目最终发布时补充。
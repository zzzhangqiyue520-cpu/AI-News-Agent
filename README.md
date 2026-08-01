# AI-News-Agent 🤖📰


## 项目介绍

AI-News-Agent 是一个基于 Python 开发的智能新闻处理 Agent 项目。

项目目标是实现一个自动化新闻处理流程：

- 自动获取新闻数据
- 对新闻内容进行整理和分析
- 使用 AI 模型生成新闻摘要
- 输出结构化新闻报告


目前项目处于开发阶段，后续将逐步加入爬虫、数据处理以及大语言模型能力。


---

## 项目功能

目前：

- ✅ Python 项目环境搭建
- ✅ Git 版本管理
- ✅ 项目基础结构搭建
- ✅ README 文档完善


计划实现：

- ⬜ 新闻网站数据采集
- ⬜ 新闻内容清洗
- ⬜ 新闻分类
- ⬜ AI 自动总结
- ⬜ Agent 工作流
- ⬜ 自动生成每日新闻报告


---

## 技术栈

开发语言：

- Python


工具：

- Git
- Github
- Linux


计划使用：

- Requests
- BeautifulSoup
- LLM API
- LangChain


---

## 项目结构

```text
AI-News-Agent

├── data                # 新闻数据存储
│
├── source              # 新闻来源相关文件
│
├── main.py             # 项目入口
│
├── requirements.txt    # Python依赖
│
├── README.md           # 项目说明
│
└── .gitignore          # Git忽略文件
环境要求

建议环境：

Python >= 3.10
Git

查看 Python 版本：

python --version

查看 Git：

git --version
安装步骤
1. 克隆项目
git clone 项目地址

进入项目目录：

cd AI-News-Agent
2. 创建虚拟环境

Windows：

python -m venv .venv

Linux：

python3 -m venv .venv
3. 激活虚拟环境

Windows PowerShell：

.venv\Scripts\activate

Linux：

source .venv/bin/activate

成功后终端会显示：

(.venv)
4. 安装依赖
pip install -r requirements.txt
使用方法

运行项目：

python main.py
开发记录

2026.08

完成 Python 环境配置
完成 Git 项目管理
完成 Github 项目上传
完成项目基础结构

后续持续开发。

未来规划
第一阶段：新闻采集
新闻网站爬虫
RSS 数据获取
API 数据获取
第二阶段：数据处理
数据清洗
内容分析
新闻分类
第三阶段：AI Agent
接入大语言模型
自动生成摘要
自动生成日报
License

This project is for learning and research purposes.

# Week2 Day1

## HTTP

浏览器访问网页：

浏览器

↓

HTTP请求

↓

服务器

↓

HTML响应


## 爬虫流程

Python程序

↓

发送HTTP请求

↓

服务器返回HTML

↓

BeautifulSoup解析

↓

保存数据


## 学习库

requests:

发送HTTP请求


BeautifulSoup:

解析HTML


## 项目完成

完成人民网新闻爬虫


实现：

- crawler.py
- parser.py
- news_manager.py


数据流程：

人民网

↓

HTML

↓

新闻标题+URL

↓

news.json


## 遇到的问题


### 问题1

find_all("a")抓取大量无关链接


解决：

定位：

div.news-item


### 问题2

浏览器显示内容比requests多

原因：

JavaScript动态加载
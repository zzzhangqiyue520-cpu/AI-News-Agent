# src/sources/base.py

from abc import ABC, abstractmethod


class BaseSource(ABC):
    """
    所有新闻源必须遵守的统一接口。

    每个新闻源都必须实现：
        fetch()

    fetch() 返回统一新闻结构。
    """

    @abstractmethod
    async def fetch(self):
        """
        获取新闻并返回统一格式的数据。
        """
        raise NotImplementedError
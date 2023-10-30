"""
Author: flwfdd
Date: 2023-10-27 20:31:26
LastEditTime: 2023-10-27 20:31:42
Description: _(:з」∠)_
"""
import json
from typing import Any
import pytz
import requests
from datetime import datetime
from newspaper import Article
import zhipuai

from config import Config

config = Config()


class News:
    def __init__(
        self, title: str, url: str, time: datetime, source: str, source_name: str
    ):
        self.title = title
        self.url = url
        self.time = time
        self.source = source
        self.source_name = source_name
        self._text = ""  # 真实的文本

    # 第一次获取text时调用
    @property
    def text(self):
        if self._text == "":
            self.generate_text()
        return self._text

    def generate_text(self):
        print("开始生成文本：", self.title)
        self._text = ""
        try:
            self._text += self.generate_summary()
        except:
            print("生成摘要失败：", self.title)

        self._text += f"来源：{self.source_name}\n"
        self._text += f"标题：{self.title}\n"
        tm = self.time.astimezone(pytz.timezone("Asia/Shanghai"))
        self._text += f"发布日期：{tm.strftime('%Y-%m-%d')}\n"
        self._text += f"原文链接：{self.url}\n"
        self._text += f"特别鸣谢 http://haobit.top 提供通知订阅服务\n"

    def generate_summary(self):
        article = Article(self.url, language="zh")
        article.download()
        article.parse()

        if article.text.strip() != "":
            s = "请根据以下材料，生成一段简洁明了的摘要，要求:严格依据通知内容总结概括，不得额外推理。\n" + article.text
            zhipuai.api_key = config.zhipuai_api_key
            r = zhipuai.model_api.invoke(
                model="chatglm_turbo",
                prompt=[{"role": "user", "content": s}],
                temperature=0.95,
                top_p=0.7,
                incremental=False,
            )
            s = ""
            s += r["data"]["choices"][0]["content"][1:-1].replace("\\n", "\n")
            s += "\n（摘要使用ChatGLM Turbo模型生成，仅供参考）\n\n"
            return s
        else:
            return ""


class NewsSource:
    def __init__(self, notices_path, sources_path):
        self.notices_path = notices_path
        self.sources_path = sources_path
        self.news_list = []

    def get_data(self, start_time):
        # 从文件或者url获取数据
        if self.notices_path.startswith("http"):
            r = requests.get(self.notices_path)
            if r.status_code != 200:
                raise Exception("获取Notices失败")
            self.notices_json = r.json()
        else:
            self.notices_json = json.load(
                open(self.notices_path, "r", encoding="utf-8")
            )

        # 获取数据源描述
        if self.sources_path.startswith("http"):
            r = requests.get(self.sources_path)
            if r.status_code != 200:
                raise Exception("获取Sources失败")
            self.sources_json = r.json()
        else:
            self.sources_json = json.load(
                open(self.sources_path, "r", encoding="utf-8")
            )
        self.sources_map = {}
        for source in self.sources_json:
            self.sources_map[source["name"]] = source

        # 生成新闻列表
        for news in self.notices_json:
            title = news["title"]
            url = news["link"]
            if news["date"].endswith("Z"):
                time = datetime.fromisoformat(news["date"][:-1] + "+00:00")
            else:
                time = datetime.fromisoformat(news["date"])
            source = news["source"]
            if source in self.sources_map and "full_name" in self.sources_map[source]:
                source_name = self.sources_map[source]["full_name"]
            else:
                source_name = source
            if time > start_time:
                self.news_list.append(News(title, url, time, source, source_name))

        self.news_list.sort(key=lambda x: x.time)
        return self.news_list

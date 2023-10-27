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
    def __init__(self, title: str, url: str, time: datetime, source: str):
        self.title = title
        self.url = url
        self.time = time
        self.source = source
        self._text = ""

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

        self._text += f"来源：{self.source}\n"
        tm = self.time.astimezone(pytz.timezone("Asia/Shanghai"))
        print(self.time,tm,tm.strftime('%Y-%m-%d'))
        self._text += f"日期：{tm.strftime('%Y-%m-%d')}\n"
        self._text += f"原文链接：{self.url}\n"
        self._text += f"特别鸣谢 http://haobit.top 提供通知列表\n"

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
    def __init__(self, path):
        self.path = path
        self.news_list = []

    def get_data(self, start_time):
        if self.path.startswith("http"):
            r = requests.get(self.path)
            if r.status_code != 200:
                raise Exception("获取数据失败")
            self.json = r.json()
        else:
            self.json = json.load(open(self.path, "r", encoding="utf-8"))

        for news in self.json:
            title = news["title"]
            url = news["link"]
            time = datetime.fromisoformat(news["date"])
            source = news["source"]
            if time > start_time:
                self.news_list.append(News(title, url, time, source))

        self.news_list.sort(key=lambda x: x.time)
        return self.news_list

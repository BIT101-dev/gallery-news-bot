"""
Author: flwfdd
Date: 2023-10-27 14:49:11
LastEditTime: 2023-10-27 23:21:29
Description: 配置文件
_(:з」∠)_
"""
from datetime import datetime
import json


# 单例模式
def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]

    return inner


@singleton
class Config:
    def __init__(self):
        self.json = json.load(open("config.json", "r", encoding="utf-8"))
        self.api_url = self.json["api_url"]
        self.notices_url = self.json["notices_url"]
        self.start_time = datetime.fromisoformat(self.json["start_time"])
        self.zhipuai_api_key = self.json["zhipuai_api_key"]
        self.bots = self.json["bots"]

    def set_start_timestamp(self, time: datetime):
        self.json["start_time"] = datetime.isoformat(time)
        self.start_time = time
        json.dump(
            self.json,
            open("config.json", "w", encoding="utf-8"),
            ensure_ascii=False,
            indent=4,
        )

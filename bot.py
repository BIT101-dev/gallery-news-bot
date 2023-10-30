"""
Author: flwfdd
Date: 2023-10-27 14:48:38
LastEditTime: 2023-10-27 15:51:07
Description: 与BIT101交互
_(:з」∠)_
"""
from hashlib import md5
import requests

from config import Config

config = Config()


def generate_insert_sql():
    bots = config.bots
    sql = '''INSERT INTO "public"."users" ("created_at", "updated_at", "sid", "password", "nickname", "motto", "identity") VALUES '''
    for bot in bots:
        sql+=f'''(NOW(), NOW(), '{bot["sid"]}', '{md5(bot["password"].encode("utf-8")).hexdigest()}', '{bot["nickname"]}', '{bot["motto"]}', 6),'''
    sql=sql[:-1]+';'
    return sql


class Bot:
    # 初始化
    def __init__(self, sid: str, password: str, sources: list):
        self.sid = sid
        self.password = password
        self.sources = sources
        self.fake_cookie = ""

    # 登录
    def login(self):
        data = {
            "sid": self.sid,
            "password": md5(self.password.encode("utf-8")).hexdigest(),
        }
        r = requests.post(config.api_url + "/user/login", json=data)
        if r.status_code != 200:
            print(r.text)
            raise Exception("登录失败")
        self.fake_cookie = r.json()["fake_cookie"]

    # 发布帖子
    def post(self, title: str, text: str, tags: list):
        if len(title) > 42:
            title = title[:41] + "…"
        data = {
            "title": title[:42],
            "text": text,
            "mids": [],
            "anonymous": False,
            "tags": tags,
            "claim_id": 0,
            "public": True,
            "plugins": "",
        }
        r = requests.post(
            config.api_url + "/posters",
            json=data,
            headers={"fake-cookie": self.fake_cookie},
        )
        if r.status_code == 401:
            self.login()
            r = requests.post(
                config.api_url + "/posters",
                json=data,
                headers={"fake-cookie": self.fake_cookie},
            )
        if r.status_code != 200:
            print(r.text)
            raise Exception("发布帖子失败")
        print("发布帖子{}: {}成功".format(r.json()["id"], title))

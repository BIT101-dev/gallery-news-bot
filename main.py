"""
Author: flwfdd
Date: 2023-10-27 14:21:29
LastEditTime: 2023-10-30 19:25:22
Description: _(:з」∠)_
"""
import argparse
import time
from bot import Bot, generate_insert_sql

from config import Config
from news import NewsSource

config = Config()

bots = []
for bot in config.bots:
    bots.append(Bot(bot["sid"], bot["password"], bot["sources"]))

news_source = NewsSource(config.notices_url, config.sources_url)


def update():
    news_list = news_source.get_data(config.start_time)

    print("开始发布：",len(news_list),"篇",time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    for news in news_list:
        flag=False
        for bot in bots:
            if news.source in bot.sources:
                try:
                    bot.post(news.title, news.text, [news.source, "通知", "新闻", "bot"])
                    if news.time > config.start_time:
                        config.set_start_timestamp(news.time)
                    flag=True
                except Exception as e:
                    print(e)
        if not flag:
            print("未发布：",news.title)


def run():
    while True:
        print("开始更新：",time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        try:
            update()
        except Exception as e:
            print(e)
        print("开始休眠：",time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        time.sleep(config.sleep_minutes * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, default="run", help="run | sql")
    args = parser.parse_args()

    if args.mode == "run":
        run()
    elif args.mode == "sql":
        print(generate_insert_sql())

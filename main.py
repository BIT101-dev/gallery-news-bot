'''
Author: flwfdd
Date: 2023-10-27 14:21:29
LastEditTime: 2023-10-28 00:44:30
Description: _(:з」∠)_
'''
"""
Author: flwfdd
Date: 2023-10-27 14:21:29
LastEditTime: 2023-10-27 21:11:49
Description: _(:з」∠)_
"""
import requests
from bot import Bot

from config import Config
from news import NewsSource

config = Config()

bots = []
for bot in config.bots:
    bots.append(Bot(bot["sid"], bot["password"], bot["sources"]))

news_source = NewsSource(config.notices_url)

def update():
    news_list = news_source.get_data(config.start_time)

    for news in news_list:
        for bot in bots:
            if news.source in bot.sources:
                bot.post(news.title,news.text,[news.source,"通知","新闻","bot"])
                config.set_start_timestamp(news.time)

update()
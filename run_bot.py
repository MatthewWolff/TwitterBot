#!/usr/bin/env python3

from TwitterBot import TwitterBot
from api_key import key


def custom_function(bot: TwitterBot) -> None:
    bot.tweet("hello")
    pass  # implement me


if __name__ == "__main__":
    bot = TwitterBot(key)
    bot.activate(bot_function=custom_function)

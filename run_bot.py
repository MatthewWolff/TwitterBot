#!/usr/bin/env python3

from TwitterBot import TwitterBot
from api_key import key

if __name__ == "__main__":
    bot = TwitterBot(key)
    bot.activate()
    # implement bot.main_function(), it will execute when the bot is active!!

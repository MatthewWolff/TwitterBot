#!/usr/bin/env python3

from collections import namedtuple
from datetime import datetime
from typing import Dict
from unittest import mock, TestCase, main as run_unit_tests

from TwitterBot import TwitterBot
from api_key import key

Tweet = namedtuple('status', ['id'])
User = namedtuple('user', ['screen_name'])


class MockTweets:
    def __init__(self, items: Dict): self.tweets = items

    def items(self): return [Tweet(k) for k in self.tweets.keys()]


class MockAPI:
    def __init__(self):
        self.user_timeline = MockTweets({'tweet1': 'contents', 'tweet2': 'contents', 'tweet3': 'contents'})
        self.favorites = MockTweets({'funny_tweet1': 'contents', 'horny_tweet2': 'contents'})

    @staticmethod
    def me(): return User('test')

    @staticmethod
    def destroy_status(tweet_id): pass

    @staticmethod
    def destroy_favorite(tweet_id): pass

    @staticmethod
    def update_status(text, in_reply_to_status_id=None): return Tweet(id=0)


api = MockAPI()


class TwitterBotTester(TestCase):

    @mock.patch('TwitterBot.tweepy.API', side_effect=lambda _: api)
    def test_init(self, mock_api):
        print('\ntesting initialization')
        bot = TwitterBot(api_keys=key, ticks=0)
        self.assertEqual((bot.api, bot.me), (api, 'test'))
        self.assertEqual(len(mock_api.call_args_list), 1)

    @mock.patch('TwitterBot.warn_input', return_value='y')
    @mock.patch('TwitterBot.tweepy.Cursor', side_effect=lambda _: api.user_timeline)
    @mock.patch('TwitterBot.tweepy.API', side_effect=lambda _: api)
    def test_clear_tweets(self, mock_api, mock_cursor, mock_input):
        print('\ntesting tweet clearing')
        bot = TwitterBot(api_keys=key, ticks=0)
        self.assertEqual(3, bot.clear_tweets())

    @mock.patch('TwitterBot.warn_input', return_value='y')
    @mock.patch('TwitterBot.tweepy.Cursor', side_effect=lambda _: api.favorites)
    @mock.patch('TwitterBot.tweepy.API', side_effect=lambda _: api)
    def test_clear_favorites(self, mock_api, mock_cursor, mock_input):
        print('\ntesting unfavoriting')
        bot = TwitterBot(api_keys=key, ticks=0)
        self.assertEqual(2, bot.clear_favorites())

    @mock.patch('TwitterBot.tweepy.API', side_effect=lambda _: api)
    @mock.patch('TwitterBot.datetime')
    def test_is_active(self, mock_datetime, mock_api):
        print('\ntesting bot sleep schedule')
        bot = TwitterBot(api_keys=key, ticks=0, active_hours=range(11, 20 + 1))  # 11am thru 8pm

        mock_datetime.now.return_value = datetime(2020, 8, 16, 23, 50)  # 11:50pm
        self.assertFalse(bot.is_active())

        mock_datetime.now.return_value = datetime(2020, 8, 16, 12, 00)  # noon
        self.assertTrue(bot.is_active())

        mock_datetime.now.return_value = datetime(2020, 8, 16, 11, 00)  # 11am
        self.assertTrue(bot.is_active())

        mock_datetime.now.return_value = datetime(2020, 8, 16, 20, 00)  # 8pm
        self.assertFalse(bot.is_active())

        bot = TwitterBot(api_keys=key, ticks=0, active_hours=[4, 5])  # 4-5am
        mock_datetime.now.return_value = datetime(2020, 8, 16, 3, 00)  # 8pm
        self.assertFalse(bot.is_active())

        mock_datetime.now.return_value = datetime(2020, 8, 16, 4, 30)  # 8pm
        self.assertTrue(bot.is_active())

    @mock.patch('TwitterBot.tweepy.API', side_effect=lambda _: api)
    def test_tweet_division(self, mock_api):
        print('\ntesting tweet division')
        bot = TwitterBot(api_keys=key, ticks=0)
        self.assertEqual(1, len(bot._divide_tweet('.' * 180)))
        self.assertEqual(1, len(bot._divide_tweet('.' * 180, at='realwoofy')))
        self.assertEqual(1, len(bot._divide_tweet('.' * 280)))
        self.assertEqual(1, len(bot._divide_tweet('.' * (280 - len('@realwoffy ')), at='realwoofy')))
        self.assertEqual(2, len(bot._divide_tweet('.' * 280, at='realwoofy')))
        self.assertEqual(2, len(bot._divide_tweet('.' * 281)))
        self.assertEqual(2, len(bot._divide_tweet('.' * 560)))
        self.assertEqual(3, len(bot._divide_tweet('.' * 561)))

    @mock.patch('builtins.open', mock.mock_open())
    @mock.patch('TwitterBot.tweepy.API', side_effect=lambda _: api)
    def test_tweet_at(self, mock_api):
        print('\ntesting tweeting')
        bot = TwitterBot(api_keys=key, ticks=0)
        self.assertEqual(bot.tweet('.' * 10), '.' * 10)
        self.assertEqual(bot.tweet('.' * 10, at="realwoofy"),
                         '#realwoofy ..........')
        self.assertEqual(bot.tweet('hey there @BarackObama', at="realwoofy", safe=True),
                         '#realwoofy hey there #BarackObama')
        self.assertEqual(bot.tweet('hey there @BarackObama', at="realwoofy", safe=False),
                         '@realwoofy hey there @BarackObama')
        self.assertEqual(bot.tweet('.' * 280), '.' * 280)
        self.assertEqual(bot.tweet('.' * 281), '.' * 280 + '... [continued]')


if __name__ == '__main__':
    run_unit_tests()

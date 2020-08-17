import sys
from datetime import datetime, timedelta
from threading import Thread
from time import sleep, strftime
from typing import Callable, Dict, List, Tuple, Union

import tweepy
from tweepy import TweepError

TWEET_MAX_LENGTH = 280


class TwitterBot:
    def __init__(self,
                 api_keys: Dict,
                 active_hours: Union[List[int], range] = range(24),
                 ticks=3  # number of ticks to display while waiting
                 ) -> None:
        self.keys = api_keys
        self.active = active_hours
        self.api, self.me = self._verify(ticks)
        self.log_file = f"{self.me}.log"

    def _verify(self, ticks) -> Tuple[tweepy.API, str]:
        """
        Verifies that the user has valid credentials for accessing Tweepy API
        :param: ticks - only present for speeding up unit-testing
        :return: a tuple containing an API object and the handle of the bot
        """

        def loading():
            for _ in range(ticks):
                print(Colors.yellow("."), end="")
                sys.stdout.flush()
                sleep(0.5)

        print(Colors.yellow("verifying credentials"), end="")
        thread = Thread(target=loading)  # lol
        thread.daemon = True  # kill this thread if program exits
        thread.start()

        api = self._authorize()
        try:
            me = api.me().screen_name
        except TweepError as e:
            raise ValueError(f"API might be disabled or you have invalid keys:\n\t{extract_tweepy_error(e)}")

        thread.join()  # lol
        print(Colors.white(" verified\n") +
              Colors.cyan("starting up bot ") + Colors.white(f"@{me}!\n"))
        return api, me  # api, the bot's handle

    def _authorize(self) -> tweepy.API:
        """
        Uses keys to create an API accessor and returns it
        :return: an API object used to access the Twitter API
        """
        auth = tweepy.OAuthHandler(self.keys["consumer_key"], self.keys["consumer_secret"])
        auth.set_access_token(self.keys["access_token"], self.keys["access_token_secret"])
        return tweepy.API(auth)

    def clear_tweets(self) -> int:
        """
        DANGER: removes all tweets from current bot account
        :returns the number of successfully deleted tweets
        """
        response = None
        while response != "y":
            response = warn_input("ARE YOU SURE YOU WANT TO ERASE ALL TWEETS? (y/n)")

        deleted = int()
        for status in tweepy.Cursor(self.api.user_timeline).items():
            try:
                self.api.destroy_status(status.id)
                deleted += 1
                print(Colors.white(f"deleted successfully - {status.id}"))
            except TweepError:
                print(Colors.red(f"failed to delete: {status.id}"))

        print(Colors.white("cleared all tweets"))
        return deleted

    def clear_favorites(self) -> int:
        """
        DANGER: removes all favorites from current bot account
        :returns the number of tweets unfavorited
        """
        response = None
        while response != "y":
            response = warn_input("ARE YOU SURE YOU WANT TO ERASE ALL FAVORITES? (y/n)")

        deleted = int()
        for status in tweepy.Cursor(self.api.favorites).items():
            try:
                self.api.destroy_favorite(status.id)
                deleted += 1
                print(Colors.white(f"unfavorited successfully - {status.id}"))
            except TweepError:
                print(Colors.red(f"failed to unfavorite: {status.id}"))

        print(Colors.white("erased all favorites"))
        return deleted

    def is_active(self) -> bool:
        """
        The bot tries not to tweet at times when no one will see
        :return: whether the bot is in its active period
        """
        current_time = datetime.now().hour
        early = self.active[0]
        late = self.active[-1]
        return early <= current_time < late

    @staticmethod
    def _divide_tweet(long_tweet: str, at: str = None) -> List[str]:
        """
        A method for exceptionally long tweets
        :rtype: the number of tweets, followed by the tweets
        :param at: the person you're responding to/at
        :param long_tweet: the long-ass tweet you're trying to make
        :return: an array of tweets
        """

        # too big!
        if len(long_tweet) >= TWEET_MAX_LENGTH * 10:
            raise ValueError(f"Attempted tweet was too large: {len(long_tweet)} characters. "
                             f"Limit is {TWEET_MAX_LENGTH * 10}")

        handle = f"@{at} " if at else ""

        def chunks(lst, chunk_size):
            """Yield successive n-sized chunks from lst."""
            for i in range(0, len(lst), chunk_size):
                yield lst[i:i + chunk_size]

        raw_tweet = handle + long_tweet
        if len(raw_tweet) <= TWEET_MAX_LENGTH:
            return [raw_tweet]
        else:
            first_tweet, surplus = raw_tweet[:TWEET_MAX_LENGTH], raw_tweet[TWEET_MAX_LENGTH:]
            other_tweets = ["".join(chunk) for chunk in chunks(list(surplus), chunk_size=TWEET_MAX_LENGTH)]
            tweets = [first_tweet] + other_tweets
            return tweets

    def activate(self, bot_function: Callable[[], None], sleep_interval: int = 60) -> None:
        while True:
            self._main_action(bot_function)
            sleep(sleep_interval)

    @staticmethod
    def is_recent(tweet, days: int = 1) -> bool:
        """
        Given a tweet, return if True/False if it's from the past day
        :param days: the number of days ago that's considered recent
        :param tweet: the tweet in question
        :return: True/False
        """
        tweeted_at = tweet.created_at - timedelta(hours=5)  # twitter is ahead by 5 hours for me (CST)
        return tweeted_at > datetime.now() - timedelta(days=days)

    def _main_action(self, bot_function: Callable[[], None]) -> None:
        """
        The method that will be run when the bot is activated
        """
        try:
            bot_function()
        except Exception as err:
            self.log_error(err)
            raise err

    def tweet(self, tweet: str, at: str = None, safe: bool = True) -> str:
        """
        General tweeting method. It will divide up long bits of text into multiple messages,
        and return the first tweet that it makes. Multi-tweets (including to other people)
        will have second and third messages made in response to self.
        :param tweet: the text to tweet
        :param at: whom the user is tweeting at
        :param safe: bots can only tweet at someone if tweeted at first. use "safe" if doing automated tweeting
        :return: the first tweet, if successful; else, empty string
        """
        if tweet.strip() == "":
            return str()

        tweets = self._divide_tweet(tweet, at)
        if len(tweets) > 0:
            prev_tweet = None
            for tweet in tweets:
                # replace @'s with #'s and convert unicode emojis before tweeting
                tweet = (tweet.replace("@", "#") if safe else tweet).encode("utf-8")
                if not prev_tweet:
                    prev_tweet = self.api.update_status(
                        tweet
                    )
                    tweets[0] = tweet.decode("utf-8")  # store for the return value
                else:
                    prev_tweet = self.api.update_status(
                        tweet,
                        in_reply_to_status_id=prev_tweet.id
                    )

            self.log(f"Tweeted: {' '.join(tweets)}")
            return tweets[0] + ("" if len(tweets) is 1 else "... [continued]")

    def log(self, activity) -> None:
        with open(self.log_file, "a") as l:
            l.write(f"{strftime('[%Y-%m-%d] @ %H:%M:%S')} {activity}\n")

    def log_error(self, error) -> None:
        self.log(Colors.red(f"ERROR => {error}"))


def warn_input(prompt: str) -> str:
    return input(Colors.red(prompt))


def extract_tweepy_error(e: TweepError):
    return e.response.reason


class Colors:
    _RED = "\033[31m"
    _RESET = "\033[0m"
    _BOLDWHITE = "\033[1m\033[37m"
    _YELLOW = "\033[33m"
    _CYAN = "\033[36m"
    _PURPLE = "\033[35m"
    _CLEAR = "\033[2J"  # clears the terminal screen

    @staticmethod
    def red(s):
        return Colors._RED + s + Colors._RESET

    @staticmethod
    def cyan(s):
        return Colors._CYAN + s + Colors._RESET

    @staticmethod
    def yellow(s):
        return Colors._YELLOW + s + Colors._RESET

    @staticmethod
    def purple(s):
        return Colors._PURPLE + s + Colors._RESET

    @staticmethod
    def white(s):
        return Colors._BOLDWHITE + s + Colors._RESET

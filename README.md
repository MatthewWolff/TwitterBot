# Twitter Bot Skeleton

## Requirements
* tweepy module (`pip install tweepy`)
* Python 3.6+ (I use special formatting from that update, sorry)
* [Twitter API credential](https://dev.twitter.com)

## Use
I've used this same skeleton on multiple twitter bots. They all perform some action after a certain time interval, whether it's checking for anyone who might have tweeted @ it or posting a tweet of its own.  

After you make a Twitter account and secure some API credentials for Tweepy (stick them in `api_key.py`), you can get going. To add functionality, just modify the `_poll()` function in `TwitterBot.py`. Feel free to add other functions to the bot that help. Reference the Tweepy API [here](http://docs.tweepy.org/en/v3.5.0/api.html) 

You can start the bot with `./run_bot.py`  

You can set the bot running in the background with 

```bash
nohup ./run_bot.py &>> output.log &
```
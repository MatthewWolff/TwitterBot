# Twitter Bot Skeleton

## Requirements
* tweepy module (`pip install tweepy`)
* Python 3.6+
* [Twitter API credential](https://dev.twitter.com)

## Usage
This bot skeleton helps to execute some user-defined function at a regular interval.  

After you make a Twitter account and secure some API credentials for Tweepy (stick them in `api_key.py`), you can get going. To add functionality, just provide a custom function to `bot.activate`. Feel free to add other functions to the bot that help. Reference the Tweepy API [here](http://docs.tweepy.org/en/v3.5.0/api.html) 

You can start the bot with `./run_bot.py`.

You can set the bot running in the background with 

```bash
nohup ./run_bot.py &>> output.log &
```

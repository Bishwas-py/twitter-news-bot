import pytz as pytz
import tweepy, json

from datetime import datetime, timedelta, timezone

import pytz

from secrets import *

tweets_to_save = [
    1514701254357782540
]



auth = tweepy.OAuthHandler(api_key, api_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth)

# set cutoff date, use utc to match twitter
cutoff_date = datetime.utcnow() - timedelta(seconds=55)
cutoff_date = cutoff_date.replace(tzinfo=pytz.UTC)


timeline = tweepy.Cursor(api.user_timeline).items()
deletion_count = 0
ignored_count = 0

for tweet in timeline:
    tweet_created_at = tweet.created_at.replace(tzinfo=pytz.UTC)
    # where tweets are not in save list and older than cutoff date
    if tweet_created_at < cutoff_date:
        if "@" not in tweet.text:
            print("Deleting %d: [%s] %s" % (tweet.id, tweet.created_at, tweet.text))
            api.destroy_status(tweet.id)

        deletion_count += 1
    else:
        ignored_count += 1
print("Deleted %d tweets, ignored %d" % (deletion_count, ignored_count))

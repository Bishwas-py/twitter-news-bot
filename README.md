# Twitter News Bot
Tweets unseful link tweets continuosly. This bot scrape data from the given rss inside `main.py > rss_feeds` array. 

## Installation
1. Go to your server/terminal, and clone this repo
2. Within the repo directory, install all the essential libraries with 
```bash
pip install -r requirements.txt
```
Done!

## Adding RRS feed
Inside `main.py` there's a list variable name `rss_feeds` add your feed URL there...

```bash
rss_feeds = [
    "https://www.westerninvestor.com/rss/british-columbia",
    "https://www.timescolonist.com/rss/bc-news",
    "https://dailyhive.com/feed/vancouver",
    "http://biv.com/rss"
]
```
## Delete all tweets at one
The `deleter.py` can help you to bulk delete tweets. `cutoff_date` variable can be use to set the date range.

## Execution
Execution is super easy

```bash
python -u main.py > err.log &
```

This will execute our twitter bot continously in the backend.

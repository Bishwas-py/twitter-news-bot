import json
import time

import tweepy
from bs4 import BeautifulSoup
import requests
from tweepy import errors

from secrets import *
import logging

import feedparser

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s | %(asctime)s | [%(levelname)s]",
    handlers=[
        logging.FileHandler("err.log"),
        logging.StreamHandler()
    ])

headers = {
    'authority': 'biv.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
}

hashtags = "#webdev #web3 #webdevelopment #javascript #python #indiedevelopment"

raw_tweet_message = """
{title}
{hashtags}
{link}
"""

logged_list = []

TWEET_MESSAGE = True

if TWEET_MESSAGE:
    auth = tweepy.OAuthHandler(api_key, api_secret)
    auth.set_access_token(access_token, access_secret)
    api = tweepy.API(auth)


def read_tweet():
    with open('twitted_messages.txt', 'r+') as file:
        twitted_messages = file.read()
        return str(twitted_messages)


def write_tweet(data):
    twitted_messages = read_tweet().splitlines()
    if data['link'] not in twitted_messages:
        with open('twitted_messages.txt', 'a+') as file:
            file.write(data['link'] + "\n")
        return "write-it"
    else:
        return "already-written"


def make_tweet(title, link, hashtags=hashtags):
    return raw_tweet_message.format(
        title=title,
        hashtags=hashtags,
        link=link
    )


def get_new_hashtags(remove_len: int):
    raw_new_hashtags = hashtags[:-remove_len]
    raw_new_hashtags_set = set(raw_new_hashtags.split(" "))
    main_hashtags_set = set(hashtags.split(" "))
    usable_new_hashtags = main_hashtags_set.intersection(raw_new_hashtags_set)
    new_hashtags = " ".join(usable_new_hashtags)
    return new_hashtags


def tweet_now(data: dict):
    # message twitted here
    if write_tweet(data) == "write-it":
        # Generate text tweet
        link = requests.post(
            "https://xoomato.com/api/make-url/",
            data={
                "original_url": data['link'],
                "key": "xoomato-create-short-uri"
            }
        ).json()
        if link.get("short_query") and link.get("success"):
            link_to_be_posted = "https://xoomato.com/" + link.get("short_query")

        if len(make_tweet(data['title'], data['link'])) > 280:
            title = data['title']

            if len(title) > 280:
                title = title[:-27]
                new_hashtags = get_new_hashtags(len(title))
            else:
                new_hashtags = get_new_hashtags(len(title) + 27)

            tweet_message = make_tweet(
                title=title,
                hashtags=new_hashtags,
                link=link_to_be_posted
            )
        else:
            tweet_message = make_tweet(
                title=data['title'],
                hashtags=hashtags,
                link=link_to_be_posted
            )
        # try:
        if TWEET_MESSAGE:
            api.update_status(tweet_message)
        logging.info(f"Newly twitted:    {data['title']}")
        # except errors.Forbidden:
        #     logging.error(f"Error on printing (Forbidden, Len: {len(tweet_message)}): {tweet_message}")
    else:
        if not data['title'] in logged_list:
            logged_list.append(data['title'])
            logging.info(f"Already Twitted:  {data['title']}")


def news_scraper(feed_url='https://www.timescolonist.com/rss/bc-news'):
    feed = feedparser.parse(feed_url)
    for entry in feed.entries:
        tweet_now(entry)


if __name__ == "__main__":
    file = open("twitted_messages.txt", "w+")
    file.close()

rss_feeds = [
    "https://dev.to/feed/tag/top"
]

while True:
    for rss_feed in rss_feeds:
        news_scraper(rss_feed)

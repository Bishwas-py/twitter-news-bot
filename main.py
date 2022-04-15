import json
import time

import tweepy
from bs4 import BeautifulSoup
import requests
from tweepy import errors

from secrets import *
import logging

logging.basicConfig(filename='err.log', filemode='w', format='%(message)s')

headers = {
    'authority': 'biv.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
}

auth = tweepy.OAuthHandler(api_key, api_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth)

hashtags = "#Yaletown #gastown #discovervancouver #burnaby #coquitlam #northvancouver #newwestminster #newwest " \
           "#westvancouver #langley #richmond #diamondtest "

raw_tweet_message = """
{title}
{hashtags}
{link}
"""

logged_list = []


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


def get_new_hashtags(remove_len:int):
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
                link=data['link']
            )
        else:
            tweet_message = make_tweet(
                title=data['title'],
                hashtags=hashtags,
                link=data['link']
            )
        try:
            api.update_status(tweet_message)
            logging.warning(f"Newly twitted:    {data['title']}")
        except errors.Forbidden:
            logging.warning(f"Error on printing (Forbidden, Len: {len(tweet_message)}): {tweet_message}")
    else:
        if not data['title'] in logged_list:
            logged_list.append(data['title'])
            logging.warning(f"Already Twitted:  {data['title']}")


def news_scraper():
    feed_url = 'https://www.timescolonist.com/rss/bc-news'
    response = requests.get(feed_url, headers=headers)
    xml_soup = BeautifulSoup(response.text)
    channel = xml_soup.find('channel')
    items_soup = channel.find_all('item')
    items = []
    for item_soup in items_soup:
        title = item_soup.find('title')
        link = item_soup.find('link')

        if not link.text:
            link = item_soup.find('guid')

        description = item_soup.find('description')
        author = item_soup.find('dc:creator')
        if not author:
            author = item_soup.find('author')

        if author:
            author = author.text

        pubdate = item_soup.find('pubdate')

        if pubdate:
            pubdate = pubdate.text

        categories_soup = item_soup.find('category')
        categories = []
        if categories_soup:
            categories = [category.text for category in categories_soup]
        media_thumbnail = item_soup.find('media:thumbnail')
        if media_thumbnail:
            media_thumbnail = media_thumbnail['url']
        data = {
            'title': title.text,
            'link': link.text,
            'description': description.text,
            'author': author,
            'pubdate': pubdate,
            'categories': categories,
            'media_thumbnail': media_thumbnail
        }
        tweet_now(data)
        items.append(
            data
        )

    result = items

    return result


if __name__ == "__main__":
    file = open("twitted_messages.txt", "w+")
    file.close()

while True:
    news_scraper()

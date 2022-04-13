import json

import tweepy
from bs4 import BeautifulSoup
import requests

from secrets import *

headers = {
    'authority': 'biv.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
}

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
        return "wrote-it"
    else:
        return "already-written"


def tweet_now(data: dict):
    tweet_message = f"""
{data['title']}
{data['link']}
"""
    # message twitted here
    if write_tweet(data) == "wrote-it":
        # Generate text tweet
        api.update_status(tweet_message)
    else:
        print("Already Twitted:  ", data['title'])


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

#!/usr/bin/env python3

# System imports
import os

import sys
import random
import string
import urllib
import json
import tempfile
import time

from pprint import pprint

# https://github.com/bear/python-twitter
import twitter
from mastodon import Mastodon

# Local imports
from local_settings import *

API_ENDPOINT = 'https://api.cognitive.microsoft.com/bing/v5.0/images/search'


class ImageDownloader():
    def __init__(self, url):
        self._url = url
        self._mime_type = ''
        self._filename = ''

    def _get_image_bytes_for_url(url):
        try:
            req = urllib.request.Request(url=url)
            resp = urllib.request.urlopen(req)
            content = resp.read()
            return content
        except:
            return []

    def download(self):
        if self._url.endswith('jpg'):
            self._mime_type = 'image/jpeg'
        elif self._url.endswith('jpeg'):
            self._mime_type = 'image/jpeg'
        elif self._url.endswith('gif'):
            self._mime_type = 'image/gif'
        elif self._url.endswith('png'):
            self._mime_type = 'image/png'
        else:
            print('Unknown image type for ' + self._url)
            return False
        image_content = ImageDownloader._get_image_bytes_for_url(self._url)
        if len(image_content) == 0:
            return False
        self._filename = tempfile.mkstemp(suffix='.tmp')[1]
        with open(self._filename, 'wb') as f:
            f.write(image_content)
        return True

    def get_filename(self):
        return self._filename

    def get_mime_type(self):
        return self._mime_type

    def finalize(self):
        try:
            os.unlink(self._filename)
        except:
            pass
        self._filename = ''


def do_post_twitter(tweet_text, image_file, image_mime_type):
    if not DO_TWITTER:
        return ''
    api = twitter.Api(consumer_key=MY_CONSUMER_KEY,
                      consumer_secret=MY_CONSUMER_SECRET,
                      access_token_key=MY_ACCESS_TOKEN_KEY,
                      access_token_secret=MY_ACCESS_TOKEN_SECRET
                      )
    status = api.PostUpdate(status=tweet_text, media=image_file)
    return "Tweeted: \"{0}\"\n".format(tweet_text)


def do_post_mastodon(tweet_text, image_file, image_mime_type):
    if not DO_MASTODON:
        return ''
    api = Mastodon(
        client_secret=CLIENT_SECRET,
        access_token=ACCESS_TOKEN,
        api_base_url='https://mastodon.cloud'
    )
    with open(image_file, 'rb') as f:
        content = f.read(-1)
    media_id = 0
    post_result = api.media_post(
        media_file=content,
        mime_type=image_mime_type,
        description=tweet_text)
    media_id = int(post_result['id'])

    if media_id != 0:
        status = api.status_post(status=tweet_text, media_ids=media_id)
    else:
        status = api.status_post(status=tweet_text)
    return "Tooted: \"{0}\"\n".format(tweet_text)


def get_word(dict_file_path):
    # Must be at least twice the size of a word in the password dictionary
    kMargin = 100
    inFile = open(dict_file_path, 'r')
    inFile.seek(0, 2)
    fileSize = inFile.tell() - kMargin

    for i in range(1, 1000):
        pointer = random.randint(0, fileSize - kMargin)
        inFile.seek(pointer)
        word = inFile.readline()  # probably does not start on a word boundry
        word = inFile.readline()[:-1]
        if (len(word) >= 1):
            break

    inFile.close()
    return word


def get_extended_search_term(searchTerm):
    extra_words = [
        "weird",
        "odd",
        "strange",
        "unusual",
        "mysterious",
        "creepy",
        "curious",
        "freaky"
    ]
    return extra_words[random.randint(0, len(extra_words))] + ' ' + searchTerm


def get_image_url(searchTerm):
    url = API_ENDPOINT + '?'
    url += 'count=1&'
    url += 'q=' + urllib.parse.quote(searchTerm, safe='')

    req = urllib.request.Request(url=url, headers={'Ocp-Apim-Subscription-Key': BING_API_KEY})
    try:
        resp = urllib.request.urlopen(req)
    except urllib.HTTPError as err:
        if 401 != err.code:
            raise err
        print("Got 401 unauthorized error")
        return 'https://netninja.com/images/error_401.png'

    content = resp.read()

    try:

        j = json.loads(content)

        return j['value'][0]['contentUrl']

    except IndexError:
        return ''
    except:
        return ''


def get_adjective_noun():
    adjective = get_word('adjective.txt')
    noun = get_word('noun.txt')
    return adjective + " " + noun


def lambda_handler(event, context):
    result = ''
    image_url = ''
    extended_search_term = ''
    if DEBUG is False:
        guess = random.choice(range(ODDS))
    else:
        guess = 0

    if guess == 0:
        for retryCounter in range(0, 10):
            adjective_noun = get_adjective_noun()
            if len(adjective_noun) > 3:
                tweet_text = adjective_noun
                extended_search_term = get_extended_search_term(adjective_noun)
                image_url = get_image_url(extended_search_term)
                if len(image_url) == 0:
                    # print("NO IMAGE FOR " + adjectiveNoun + ". RETRYING.")
                    time.sleep(2)  # don't hammer the server
                    continue
                # if (len(image_url) > 0):
                #    tweet_text += "\n\n" + image_url
                print(adjective_noun)
                print(extended_search_term)
                print(image_url)

                downloader = ImageDownloader(image_url)
                if downloader.download() is False:
                    print('Bad download. Retrying.')
                    continue

                if DEBUG is False:
                    if DO_TWITTER:
                        try:
                            do_post_twitter(tweet_text, downloader.get_filename(), downloader.get_mime_type())
                        except:
                            result += "Error posting to Twitter\n"
                    if DO_MASTODON:
                        try:
                            do_post_mastodon(tweet_text, downloader.get_filename(), downloader.get_mime_type())
                        except:
                            result += "Error posting to Mastodon\n"
                    # Only finalize in non-debug, otherwise we may want to inspect the download.
                    downloader.finalize()
                else:
                    result += tweet_text
                    result += "\n"
                    result += image_url
                    result += "\n"
                    result += downloader.get_filename()
                    result += "\n"
                    result += str(downloader.get_mime_type())


                break
    else:
        result += str(guess) + " No, sorry, not this time.\n"  # message if the random number fails.

    return {'message': result, 'url': image_url, 'extended_search_term': extended_search_term}

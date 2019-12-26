#!/usr/bin/env python3

import os
import sys
import random
import string
import urllib
import json
import time
# https://github.com/halcy/Mastodon.py
# https://mastodonpy.readthedocs.io/en/latest/
from mastodon import Mastodon
from local_settings import *

API_ENDPOINT = 'https://api.cognitive.microsoft.com/bing/v5.0/images/search'

def connect():
    api = Mastodon(
        client_secret = CLIENT_SECRET,
        access_token = ACCESS_TOKEN,
        api_base_url = 'https://mastodon.cloud'
        )
    return api

def GetWord(dictFilePath):
    # Must be at least twice the size of a word in the password dictionary
    kMargin = 100
    inFile = open(dictFilePath, 'r')
    inFile.seek(0, 2)
    fileSize = inFile.tell() - kMargin

    for i in range(1, 1000):
        pointer = random.randint(0, fileSize - kMargin)
        inFile.seek(pointer)
        word = inFile.readline()    # probably does not start on a word boundry
        word = inFile.readline()[:-1]
        if (len(word) >= 1):
            break

    inFile.close()
    return word

def GetImageURL(searchTerm):
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

def GetAdjectiveNoun():
    adjective = GetWord('adjective.txt')
    noun = GetWord('noun.txt')
    return adjective + " " + noun

def lambda_handler(event, context):
    result = ''
    image_url = ''
    if DEBUG==False:
        guess = random.choice(range(ODDS))
    else:
        guess = 0

    if guess == 0:
        for retryCounter in range(0, 10):
            adjectiveNoun = GetAdjectiveNoun()
            if (len(adjectiveNoun) > 3):
                tweet_text = adjectiveNoun
                image_url = GetImageURL(adjectiveNoun)
                if (len(image_url) == 0):
                    #print "NO IMAGE FOR " + adjectiveNoun + ". RETRYING."
                    time.sleep(2) # don't hammer the server
                    continue
                #if (len(image_url) > 0):
                #    tweet_text += "\n\n" + image_url
                print(adjectiveNoun)
                print(image_url)

                # todo: image search for picture and attach?

                if DEBUG == False:
                    result += DoPost(tweet_text, image_url)
                else:
                    result += tweet_text
                    result += ''
                break
    else:
        result += str(guess) + " No, sorry, not this time.\n" #message if the random number fails.

    return {'message': result, 'url': image_url}

def DoPost(tweet_text, image_url):
    result = ''
    api = connect()
    local_filename = ''
    media_id = 0
    if (len(image_url) > 0):
        req = urllib2.Request(image_url)
        resp = urllib2.urlopen(req)
        content = resp.read()
        image_mime_type = resp.info().type
        print("mime_type is " + image_mime_type)

        post_result = api.media_post(
                media_file = content,
                mime_type = image_mime_type,
                description = tweet_text)
        media_id = (int) (post_result['id'])


    if (media_id != 0):
        status = api.status_post(
                status = tweet_text,
                media_ids = media_id)
    else:
        status = api.status_post(
                status = tweet_text)
    result += 'Tweeted: '
    result += tweet_text
    result += ''
    return result


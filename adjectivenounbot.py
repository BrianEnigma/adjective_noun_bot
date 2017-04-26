#!/usr/bin/env python

import sys
import random
import string
import twitter
from local_settings import *

def connect():
    api = twitter.Api(consumer_key=MY_CONSUMER_KEY,
                          consumer_secret=MY_CONSUMER_SECRET,
                          access_token_key=MY_ACCESS_TOKEN_KEY,
                          access_token_secret=MY_ACCESS_TOKEN_SECRET)
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

def GetAdjectiveNoun():
    adjective = GetWord('adjective.txt')
    noun = GetWord('noun.txt')
    return adjective + " " + noun

def lambda_handler(event, context):
    result = ''
    if DEBUG==False:
        guess = random.choice(range(ODDS))
    else:
        guess = 0

    if guess == 0:
        adjectiveNoun = GetAdjectiveNoun()
        if (len(adjectiveNoun) > 3):
            tweet_text = adjectiveNoun

            # todo: image search for picture and attach?

            if DEBUG == False:
                api=connect()
                status = api.PostUpdate(tweet_text)
                result += 'Tweeted: '
                result += tweet_text
                result += ''
            else:
                result += tweet_text
                result += ''
    else:
        result += str(guess) + " No, sorry, not this time.\n" #message if the random number fails.

    return {'message': result}


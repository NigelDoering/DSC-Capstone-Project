import pandas as pd
import requests
import os
import gzip
import shutil
import json
from flatten_dict import flatten
from twarc import Twarc
import logging
import tweepy
import csv
import pickle


# Credit to: https://gist.github.com/yanofsky/5436496

def get_data(logger, consumer_key: str, consumer_secret_key: str, 
    access_token: str, access_token_secret: str, bearer_token: str, 
    output_path: str, exclude_replies: bool, include_rts: bool, max_recent_tweets: float, tweet_ids=[]):
    '''
    Retrieve user tweets and write to csv.
    '''
    # Tweepy Authorization
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret_key)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    # Specific tweets
    for tweet_id in tweet_ids:
        status = api.get_status(tweet_id)
        logger.info(type(status))
        fn = os.path.join(output_path, 'tweet_{}.csv'.format(tweet_id))
        tweet_info = {
            'id': status.id,
            'created_at': status.created_at,
            'user/id': status.user.id,
            'text': status.text
        }
        user_ids = []
        retweets_list = api.retweets(tweet_id)
        for retweet in retweets_list:
            user_ids.append(retweet.user.id)
        tweet_info['user_ids'] = user_ids
        f = open(fn, 'wb')
        pickle.dump(tweet_info, f)

        # Get retweeters
        retweets_list = api.retweets(tweet_id)
        for retweet in retweets_list:
            user_id = retweet.user.id
            logger.info('Collecting user {} tweets'.format(user_id))

            #initialize a list to hold all the tweepy Tweets
            alltweets = []  

            #make initial request for most recent tweets (200 is the maximum allowed count)
            new_tweets = api.user_timeline(user_id, count=200, exclude_replies=exclude_replies, include_rts=include_rts)

            #save most recent tweets
            alltweets.extend(new_tweets)

            if len(alltweets) != 0:
                #save the id of the oldest tweet less one
                oldest = alltweets[-1].id - 1

                # keep grabbing tweets until there are no tweets left to grab
                while len(new_tweets) > 0 and len(alltweets) < max_recent_tweets:
                    logger.info('getting tweets before {}'.format(oldest))
                    
                    #all subsiquent requests use the max_id param to prevent duplicates
                    new_tweets = api.user_timeline(user_id, count=200, exclude_replies=exclude_replies, include_rts=include_rts, max_id=oldest)
                    
                    #save most recent tweets
                    alltweets.extend(new_tweets)
                    
                    #update the id of the oldest tweet less one
                    oldest = alltweets[-1].id - 1

                    logger.info('{} tweets downloaded so far'.format(len(alltweets)))
                    

                alltweets = alltweets[:max_recent_tweets]
        
            #transform the tweepy tweets into a 2D array that will populate the csv 
            outtweets = [[tweet.id_str, tweet.created_at, tweet.text] for tweet in alltweets]

            if output_path:
                fn = os.path.join(output_path, 'user_{}_tweets.csv'.format(user_id))
                with open(fn, 'w') as f:
                    writer = csv.writer(f)
                    writer.writerow(["id", "created_at", "text"])
                    writer.writerows(outtweets)

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



def get_data(logger, consumer_key: str, consumer_secret_key: str, 
    access_token: str, access_token_secret: str, bearer_token: str, 
    repo_path: str, 
    output_path: str, user_ids=[]):
    '''
    Retrieve user tweets and write to csv.
    '''
    # Tweepy Authorization
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret_key)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    # User tweets
    logger.info('Collecting user tweets')
    for user_id in user_ids:
        statuses = api.user_timeline(user_id, count=10000, exclude_replies=True)
        list_dicts = []
        for status in statuses:
            new = {}
            new['entities/hashtags'] = status.entities['hashtags']
            new['id'] = status.id
            new['created_at'] = status.created_at
            new['user/id'] = status.user.id
            new['text'] = status.text
            new['retweet_count'] = status.retweet_count
            new['favorite_count'] = status.favorite_count
            list_dicts.append(new)

        df = pd.DataFrame(list_dicts[:])
        if output_path:
            logger.info('Writing to {}'.format(os.path.join(output_path, 'user_{}_tweets.csv'.format(user_id))))
            df.to_csv(os.path.join(output_path, 'user_{}_tweets.csv'.format(user_id)))
    logger.info('Collected user tweets')

    

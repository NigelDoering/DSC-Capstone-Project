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
    repo_path: str, start_date: str, end_date: str, clean=False, output_path=None, frac=None, user_ids=[], tweet_ids=[]):
    '''
    Retrieve Coronavirus tweets from multiple days from GitHub repo.
    Returns pandas dataframe of hydrated tweets.
    @repo_path: path to the repo.
    @start_date: start date of tweets (inclusive)
    @end_date: end date of tweets (exclusive)
    @clean: uses the cleaned set which does not include retweets, default False.
    @output_path: if provided, writes dataframe to output path.
    @frac: if provided, uses only this fraction of the tweets.
    '''
    # Tweets
    logger.info('Collecting Coronavirus Pancea Lab tweets')
    if len(start_date) != 0 and len(end_date) != 0:
        dfs = []
        lst = list(pd.date_range(start=start_date,end=end_date))
        dates = [date_obj.strftime('%Y-%m-%d') for date_obj in lst]

        # Gather tweet IDS
        for date in dates:
            # Unzip tsv.gz file
            logger.info('Processing {}...'.format(date))
            fp = repo_path
            rp = 'covid19_twitter/dailies/{}'.format(date)
            if clean:
                fn = '{}_clean-dataset.tsv.gz'.format(date)
            else:
                fn = '{}-dataset.tsv.gz'.format(date)
                fp = repo_path
                rp = 'covid19_twitter/dailies/{}'.format(date)
            if clean:
                fn = '{}_clean-dataset.tsv.gz'.format(date)
            else:
                fn = '{}-dataset.tsv.gz'.format(date)

            filename = os.path.join(fp, rp, fn)
            assert os.path.isfile(filename), "Make sure that repo path and date is valid {}".format(filename) 

            with gzip.open(filename, 'rb') as f_in:
                with open(filename[:-3], 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # Read in tsv
            df = pd.read_csv(filename[:-3], sep='\t')

            # Append tweet IDs
            if frac:
                dfs.append(df.sample(frac=frac)['tweet_id'])
                logger.info('Adding {} tweets'.format(int(len(df)*frac)))
            else:
                dfs.append(df['tweet_id'])
                logger.info('Adding {} tweets'.format(len(df)))
        df = pd.concat(dfs)
            
        # write tweet ids to txt file
        tweet_id_fp = os.path.join(output_path, start_date + '-' + end_date +'.txt')
        logger.info('Writing tweets to txt file {}...'.format(tweet_id_fp))
        df.to_csv(tweet_id_fp, index=False, header=False)

        # Use library
        t = Twarc(consumer_key, consumer_secret_key, access_token, access_token_secret)
        list_dicts = []
        for tweet in t.hydrate(open(os.path.join(output_path, start_date + '-' + end_date +'.txt'))):
            orig = flatten(tweet, reducer='path')
            new = {}
            for col in ['entities/hashtags', 'id', 'created_at', 'user/id']:
                new[col] = orig[col]
            list_dicts.append(new)
            # print(new)

        df = pd.DataFrame(list_dicts[:])
        
        if output_path:
            logging.info('Writing to {}'.format(os.path.join(output_path, 'data.csv')))
            df.to_csv(os.path.join(output_path, 'data.csv'))
    logger.info('Collected Coronavirus Pancea Lab tweets')

    # Tweepy Authorization
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret_key)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    # User tweets
    logger.info('Collecting user tweets')
    for user_id in user_ids:
        statuses = api.user_timeline(user_id, count=1000)
        list_dicts = []
        for status in statuses:
            new = {}
            new['entities/hashtags'] = status.entities['hashtags']
            new['id'] = status.id
            new['created_at'] = status.created_at
            new['user/id'] = status.user.id
            list_dicts.append(new)

        df = pd.DataFrame(list_dicts[:])
        if output_path:
            logger.info('Writing to {}'.format(os.path.join(output_path, 'user_{}_tweets.csv'.format(user_id))))
            df.to_csv(os.path.join(output_path, 'user_{}_tweets.csv'.format(user_id)))
    logger.info('Collected user tweets')

    # Famous Tweets
    logger.info('Collecting major tweets')
    for tweet_id in tweet_ids:
        status = api.get_status(tweet_id)
        status_data = []
        status_data.append(['username', status.user.name])
        status_data.append(['text', status.text])
        status_data.append(['favorite_count', status.favorite_count])
        status_data.append(['retweet_count', status.retweet_count])
        results = api.retweets(tweet_id, 100) 
        user_ids = []
        for status in results:
            user_ids.append(status.user.id)
        status_data.append(['user_ids', user_ids])
        s = pd.DataFrame(status_data, columns=['cat', 'data'])
        s.to_csv(os.path.join(output_path, 'tweet_{}.csv'.format(tweet_id)))
        logger.info(len(user_ids))
        for user_id in user_ids:
            logger.info('getting {} tweets'.format(user_id))
            statuses = api.user_timeline(user_id, count=1000)
            list_dicts = []
            for status in statuses:
                new = {}
                new['entities/hashtags'] = status.entities['hashtags']
                new['id'] = status.id
                new['created_at'] = status.created_at
                new['user/id'] = status.user.id
                list_dicts.append(new)

            df = pd.DataFrame(list_dicts[:])
            if output_path:
                logger.info('Writing to {}'.format(os.path.join(output_path, 'user_{}_tweets.csv'.format(user_id))))
                df.to_csv(os.path.join(output_path, 'user_{}_tweets.csv'.format(user_id)))
    logger.info('Collected major tweets')

    

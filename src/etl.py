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
from os import listdir
from os.path import isfile, join

def get_data(logger, preprocessed_data_path: str, output_data_path: str, dims: list, labels: dict,
    consumer_key: str, consumer_secret_key: str, access_token: str, access_token_secret: str, bearer_token: str):
    logger.info('getting data')

    fns = [filename for filename in listdir(preprocessed_data_path) if filename.endswith(".csv") ]
    dir = preprocessed_data_path

    li = []
    for fn in fns:
        logger.info('reading in {}'.format(fn))
        df = pd.read_csv(os.path.join(dir, fn), index_col=None, usecols=['text'], header=0)
        for i in range(len(dims)):
            label = labels[fn.replace('.csv', '')][i]
            df[dims[i]] = pd.Series([label]*df.shape[0])
        li.append(df)

    df = pd.concat(li, axis=0, ignore_index=True)
    os.makedirs(output_data_path, exist_ok=True)
    df.to_csv(os.path.join(output_data_path, 'data.csv'))

    logger.info('finished getting data and wrote data to {}'.format(os.path.join(output_data_path, 'data.csv')))
    return


    # # Tweepy
    # auth = tweepy.OAuthHandler(consumer_key, consumer_secret_key)
    # auth.set_access_token(access_token, access_token_secret)
    # api = tweepy.API(auth)

    # files = [f for f in listdir(training_data_id_path) if isfile(os.path.join(training_data_id_path, f))]


    # text = []
    # for fn in files:
    #     succ = 0
    #     fail = 0
    #     f = open(os.path.join(training_data_id_path, fn), 'rb')
    #     lines = f.readlines()
    #     tot_tweets = len(lines)
    #     logger.info('Starting {} with {} tweets'.format(fn, tot_tweets))
    #     for tweet_id in lines:
    #         try:
    #             status = api.get_status(tweet_id)
    #             text.append(status.text)
    #             succ += 1
    #         except:
    #             fail += 1
    #         if (succ+fail) % 100 == 0:
    #             logger.info('{}/{} tweets hydrated'.format(succ+fail, tot_tweets))
    #     f.close()
    #     logger.info('Finished {} Success: {} Fail: {}'.format(fn, succ, fail))

    # df = pd.DataFrame({'text': text})
    # df.to_csv(os.path.join(training_data_path, 'data.csv'))


    # TWARC
    # hydrating news source files
    # encoding='utf-8'
    # t = Twarc(consumer_key, consumer_secret_key, access_token, access_token_secret)
    # files = [f for f in listdir(training_data_id_path) if isfile(os.path.join(training_data_id_path, f))]
    # list_dicts = []
    # for file in files:
    #     try:
    #         count = len(open(os.path.join(training_data_id_path, file)).readlines())
    #     except:
    #         count = "unknown"
    #     logger.info('{} has {} tweets'.format(file, count))

    #     name = file.replace('.txt', '')
    #     ct = 0
    #     for tweet in t.hydrate(open(os.path.join(training_data_id_path, file), 'r')):
    #         orig = flatten(tweet, reducer='path')
    #         new = {}
    #         for col in ['full_text']:
    #             new[col] = orig[col]
    #         for i in range(len(dims)):
    #             new[dims[i]] = labels[name][i]
    #         list_dicts.append(new)
    #         ct += 1
    #         if ct % 1000 == 0:
    #             logger.info('finished {}/{} of {} tweets'.format(ct, count, file))
    #     logger.info('finished hydrating tweets from {}'.format(file))

    # # writing to dataframe
    # df = pd.DataFrame(list_dicts[:])
    # df.to_csv(os.path.join(training_data_path, 'data.csv'))
    # logger.info('wrote {} dataframe of training data'.format(df.shape))
    # logger.info('finished getting data')
    # return


# def get_data(logger, pancea_tweets: bool, major_tweets: bool, repo_path: str, start_date: str, end_date: str, clean: bool,
#     output_path: str, frac: float, exclude_replies: bool, include_rts: bool,
#     max_recent_tweets: float, consumer_key: str, consumer_secret_key: str, 
#     access_token: str, access_token_secret: str, bearer_token: str, tweet_ids=[]):
#     if pancea_tweets:
#         get_data_pancea_tweets(logger, consumer_key, consumer_secret_key, 
#         access_token, access_token_secret, bearer_token, 
#         repo_path, start_date, end_date, clean, output_path, frac)

#     if major_tweets:
#         get_data_major_tweets(logger, consumer_key, consumer_secret_key,
#         access_token, access_token_secret, bearer_token,
#         output_path, exclude_replies, include_rts, max_recent_tweets, tweet_ids)

#     return

# # Credit to: https://gist.github.com/yanofsky/5436496 for the Major tweets
# def get_data_major_tweets(logger, consumer_key: str, consumer_secret_key: str, 
#     access_token: str, access_token_secret: str, bearer_token: str, 
#     output_path: str, exclude_replies: bool, include_rts: bool, max_recent_tweets: float, tweet_ids=[]):
#     '''
#     Retrieve user tweets and write to csv.
#     '''
#     logger.info("collecting major tweet data")
#     # Tweepy Authorization
#     auth = tweepy.OAuthHandler(consumer_key, consumer_secret_key)
#     auth.set_access_token(access_token, access_token_secret)
#     api = tweepy.API(auth)

#     # Specific tweets
#     for tweet_id in tweet_ids:
#         status = api.get_status(tweet_id)
#         logger.info(type(status))
#         fn = os.path.join(output_path, 'tweet_{}.csv'.format(tweet_id))
#         tweet_info = {
#             'id': status.id,
#             'created_at': status.created_at,
#             'user/id': status.user.id,
#             'text': status.text,
#             'entities/hashtags': status.entities['hashtags'] # see if this works
#         } 
#         user_ids = {}
#         retweets_list = api.retweets(tweet_id)
#         for retweet in retweets_list:
#             user_ids[str(retweet.user.id)] = None
#             # user_ids.append(retweet.user.id)
#         tweet_info['user_ids'] = user_ids
#         f = open(fn, 'wb')
#         pickle.dump(tweet_info, f)

#         # Get retweeters
#         retweets_list = api.retweets(tweet_id)
#         for retweet in retweets_list:
#             user_id = retweet.user.id
#             logger.info('Collecting user {} tweets'.format(user_id))

#             #initialize a list to hold all the tweepy Tweets
#             alltweets = []  

#             #make initial request for most recent tweets (200 is the maximum allowed count)
#             new_tweets = api.user_timeline(user_id, count=200, exclude_replies=exclude_replies, include_rts=include_rts)

#             #save most recent tweets
#             alltweets.extend(new_tweets)

#             if len(alltweets) != 0:
#                 #save the id of the oldest tweet less one
#                 oldest = alltweets[-1].id - 1

#                 # keep grabbing tweets until there are no tweets left to grab
#                 while len(new_tweets) > 0 and len(alltweets) < max_recent_tweets:
#                     logger.info('getting tweets before {}'.format(oldest))
                    
#                     #all subsiquent requests use the max_id param to prevent duplicates
#                     new_tweets = api.user_timeline(user_id, count=200, exclude_replies=exclude_replies, include_rts=include_rts, max_id=oldest)
                    
#                     #save most recent tweets
#                     alltweets.extend(new_tweets)
                    
#                     #update the id of the oldest tweet less one
#                     oldest = alltweets[-1].id - 1

#                     logger.info('{} tweets downloaded so far'.format(len(alltweets)))
                    

#                 alltweets = alltweets[:max_recent_tweets]
        
#             #transform the tweepy tweets into a 2D array that will populate the csv 
#             outtweets = [[tweet.id_str, tweet.created_at, tweet.text, tweet.entities['hashtags']] for tweet in alltweets]

#             if output_path:
#                 fn = os.path.join(output_path, 'user_{}_tweets.csv'.format(user_id))
#                 with open(fn, 'w') as f:
#                     writer = csv.writer(f)
#                     writer.writerow(["id", "created_at", "text", "entities/hashtags"])
#                     writer.writerows(outtweets)
#     logger.info("collected major tweet data")

# def get_data_pancea_tweets(logger, consumer_key: str, consumer_secret_key: str, 
#     access_token: str, access_token_secret: str, bearer_token: str, 
#     repo_path: str, start_date: str, end_date: str, clean: bool, output_path: str, frac: float):
#     '''
#     Retrieve Coronavirus tweets from multiple days from GitHub repo and write to csv.
#     '''
#     # Tweets
#     logger.info('Collecting Coronavirus Pancea Lab tweets')
#     if len(start_date) != 0 and len(end_date) != 0:
#         dfs = []
#         lst = list(pd.date_range(start=start_date,end=end_date))
#         dates = [date_obj.strftime('%Y-%m-%d') for date_obj in lst]

#         # Gather tweet IDS
#         for date in dates:
#             # Unzip tsv.gz file
#             logger.info('Processing {}...'.format(date))
#             fp = repo_path
#             rp = 'covid19_twitter/dailies/{}'.format(date)
#             if clean:
#                 fn = '{}_clean-dataset.tsv.gz'.format(date)
#             else:
#                 fn = '{}-dataset.tsv.gz'.format(date)
#                 fp = repo_path
#                 rp = 'covid19_twitter/dailies/{}'.format(date)
#             if clean:
#                 fn = '{}_clean-dataset.tsv.gz'.format(date)
#             else:
#                 fn = '{}-dataset.tsv.gz'.format(date)

#             filename = os.path.join(fp, rp, fn)
#             assert os.path.isfile(filename), "Make sure that repo path and date is valid {}".format(filename) 

#             with gzip.open(filename, 'rb') as f_in:
#                 with open(filename[:-3], 'wb') as f_out:
#                     shutil.copyfileobj(f_in, f_out)

#             # Read in tsv
#             df = pd.read_csv(filename[:-3], sep='\t')

#             # Append tweet IDs
#             if frac:
#                 dfs.append(df.sample(frac=frac)['tweet_id'])
#                 logger.info('Adding {} tweets'.format(int(len(df)*frac)))
#             else:
#                 dfs.append(df['tweet_id'])
#                 logger.info('Adding {} tweets'.format(len(df)))
#         df = pd.concat(dfs)
            
#         # write tweet ids to txt file
#         tweet_id_fp = os.path.join(output_path, start_date + '-' + end_date +'.txt')
#         logger.info('Writing tweets to txt file {}...'.format(tweet_id_fp))
#         df.to_csv(tweet_id_fp, index=False, header=False)

#         # Use library
#         t = Twarc(consumer_key, consumer_secret_key, access_token, access_token_secret)
#         list_dicts = []
#         for tweet in t.hydrate(open(os.path.join(output_path, start_date + '-' + end_date +'.txt'))):
#             orig = flatten(tweet, reducer='path')
#             new = {}
#             for col in ['entities/hashtags', 'id', 'created_at', 'user/id']:
#                 new[col] = orig[col]
#             list_dicts.append(new)
#             # print(new)

#         df = pd.DataFrame(list_dicts[:])
        
#         if output_path:
#             logging.info('Writing to {}'.format(os.path.join(output_path, 'data.csv')))
#             df.to_csv(os.path.join(output_path, 'data.csv'))
#     logger.info('Collected Coronavirus Pancea Lab tweets')

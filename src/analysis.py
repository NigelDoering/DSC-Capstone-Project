import pandas as pd
import numpy as np
import requests
import os
import gzip
import shutil
import json
from flatten_dict import flatten
from twarc import Twarc
import logging
import re

from eda import get_top_hashtags

def compute_hashtag_polarities(logger, data, top_hashtags, outdir, n_hashtags, marker_hashtags, case_sensitive):
    logger.info('starting polarities')
    #top_hashtags = get_top_hashtags(logger, data, outdir, n_hashtags, case_sensitive)
    top_hashtags['baseline_rate_occ'] = top_hashtags['n_occ'] / data.shape[0]

    regstr = '|'.join(marker_hashtags)
    subset = data[data['entities/hashtags'].str.contains(regstr, case=case_sensitive)]
    logger.info('Obtained subset data')

    def get_hashtags(input_str):
        if type(input_str) != str:
            return []
        if not case_sensitive:
            input_str = input_str.lower()
        return [elem[9:-1] for elem in re.findall("'text': '\w+'", input_str)]
    subset['list_hashtags'] = subset['entities/hashtags'].apply(get_hashtags)
    subset_hashtag_counts = pd.Series(subset['list_hashtags'].sum()).value_counts()
    logger.info('Obtained subset hashtag counts')
    
    logger.info(top_hashtags.shape)
    top_hashtags = top_hashtags.reset_index()
    def get_subset_occ(x):
        try:
            return subset_hashtag_counts[x]
        except:
            return 0
    top_hashtags['subset_occ'] = top_hashtags['index'].apply(get_subset_occ)
    top_hashtags['subset_rate_occ'] = top_hashtags['subset_occ'] / subset.shape[0]
    top_hashtags = top_hashtags.set_index('index')
    top_hashtags = top_hashtags.drop(columns=['subset_occ'])
    top_hashtags['polarity'] = (top_hashtags['subset_rate_occ'] - top_hashtags['baseline_rate_occ'])/top_hashtags['baseline_rate_occ']
    logger.info(top_hashtags.columns)
    top_hashtags = top_hashtags[~top_hashtags.index.isin(marker_hashtags)]

    s = pd.Series({'total_tweets': data.shape[0], 'subset_tweets': subset.shape[0]})

    top_hashtags.to_csv(os.path.join(outdir, 'hashtag_polarities.csv'))
    s.to_csv(os.path.join(outdir, 'metrics.csv'))
    logger.info('finished polarities')
    return top_hashtags

def compute_user_polarities(logger, user_dfs, top_hashtags, outdir, case_sensitive, output=True):
    logger.info('starting user polarities')
    def get_hashtags(input_str):
        if type(input_str) != str:
            return []
        if not case_sensitive:
            input_str = input_str.lower()
        return [elem[9:-1] for elem in re.findall("'text': '\w+'", input_str)]

    user_dfs_hashtag_counts = []
    user_polarities = {}
    for user_df in user_dfs:
        user_id = user_df['user/id'].values[0]
        user_df['list_hashtags'] = user_df['entities/hashtags'].apply(get_hashtags)
        user_df_hashtag_count = pd.DataFrame(pd.Series(user_df['list_hashtags'].sum()).value_counts()).rename(columns={0: 'ct'}).reset_index()
        user_dfs_hashtag_counts.append(user_df_hashtag_count)
        df = user_df_hashtag_count.join(top_hashtags, on='index', how='left').dropna()
        user_polarity = (df['polarity']*df['ct']).sum() / df['ct'].sum()
        user_polarities[user_id] = user_polarity

    df = pd.DataFrame({'user/id': list(user_polarities.keys()), 'polarity': list(user_polarities.values())})
    if output:
        df.to_csv(os.path.join(outdir, 'user_polarities.csv'))
    logger.info('finished user polarities')
    return df

def compute_tweet_polarities(logger, tweet_user_dfss, user_dfs, top_hashtags, tweet_ids, outdir, case_sensitive):
    logger.info('computing tweet polarities')
    i = 0
    for tweet_user_dfs in tweet_user_dfss:
        logger.info('number of retweeters for this tweet is {}'.format(len(tweet_user_dfs)))
        df = compute_user_polarities(logger, tweet_user_dfs, top_hashtags, outdir, case_sensitive, output=False)
        logger.info(df)
        df['polarity'] = np.log(df.polarity + 2)
        ax = df['polarity'].plot(kind='hist', title='Users who Retweeted - Log(polarity+2)')
        logger.info('number of users with null polarities is {}'.format(df['polarity'].isnull().sum()))
        fig = ax.get_figure()
        fig.savefig(os.path.join(outdir, 'tweets_polarity_histogram_{}.png'.format(tweet_ids[i])))
        fig.clf()
        i += 1


    logger.info('computed tweet polarities')
    return 



def compute_stats(logger, data, top_hashtags, user_dfs, tweet_user_dfss, outdir, **kwargs):
    os.makedirs(outdir, exist_ok=True)
    cfg = {}
    for key, value in kwargs.items():
        cfg[key] = value

    top_hashtags = compute_hashtag_polarities(logger, data, top_hashtags, outdir, cfg['n_hashtags'], cfg['marker_hashtags'], cfg['case_sensitive'])
    compute_user_polarities(logger, user_dfs, top_hashtags, outdir, cfg['case_sensitive'])
    compute_tweet_polarities(logger, tweet_user_dfss, user_dfs, top_hashtags, cfg['tweet_ids'], outdir, cfg['case_sensitive'])
    return

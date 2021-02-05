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

def get_top_hashtags(logger, data, outdir, n_hashtags, case_sensitive):
    logger.info('Start generating chart of top hashtags used')
    def get_hashtags(input_str):
        if type(input_str) != str:
            return []
        if not case_sensitive:
            input_str = input_str.lower()
        return [elem[9:-1].replace('_', '').replace('ー', '') for elem in re.findall("'text': '\w+'", input_str)]
    data['list_hashtags'] = data['entities/hashtags'].apply(get_hashtags)
    hashtag_counts = pd.Series(data['list_hashtags'].sum()).value_counts()
    df = pd.DataFrame(hashtag_counts.sort_values(ascending=False)[:n_hashtags]).rename(columns={0: 'n_occ'})
    df.to_csv(os.path.join(outdir, 'top_hashtags.csv'))
    logger.info('Finish generating chart of top hashtags used')
    return df

def compute_hashtag_polarities(logger, data, top_hashtags, outdir, n_hashtags, marker_hashtags, case_sensitive):
    logger.info('Start computing hashtag polarities')
    top_hashtags['baseline_rate_occ'] = top_hashtags['n_occ'] / data.shape[0]

    reset = False
    for dim in marker_hashtags.keys():
        logger.info('computing {} dimension'.format(dim))
        pos_list = marker_hashtags[dim][0]
        neg_list = marker_hashtags[dim][1]
        for i in range(2):
            if i == 0:
                regstr = '|'.join(pos_list)
            else:
                regstr = '|'.join(neg_list)
            #regstr = marker_hashtag
            subset = data[data['entities/hashtags'].str.contains(regstr, case=case_sensitive)]
            logger.info('Obtained subset data')

            def get_hashtags(input_str):
                if type(input_str) != str:
                    return []
                if not case_sensitive:
                    input_str = input_str.lower()
                return [elem[9:-1].replace('_', '').replace('ー', '') for elem in re.findall("'text': '\w+'", input_str)]
            subset['list_hashtags'] = subset['entities/hashtags'].apply(get_hashtags)
            subset_hashtag_counts = pd.Series(subset['list_hashtags'].sum()).value_counts()

            if not reset:
                top_hashtags = top_hashtags.reset_index()
                reset = True
            def get_subset_occ(x):
                try:
                    return subset_hashtag_counts[x]
                except:
                    return 0
            if i == 0:
                top_hashtags['subset_occ_pro_{}'.format(dim)] = top_hashtags['index'].apply(get_subset_occ)
                top_hashtags['subset_rate_occ_pro_{}'.format(dim)] = top_hashtags['subset_occ_pro_{}'.format(dim)] / subset.shape[0]
            else:
                top_hashtags['subset_occ_neg_{}'.format(dim)] = top_hashtags['index'].apply(get_subset_occ)
                top_hashtags['subset_rate_occ_neg_{}'.format(dim)] = top_hashtags['subset_occ_neg_{}'.format(dim)] / subset.shape[0]
    top_hashtags = top_hashtags.fillna(0)
    top_hashtags.to_csv(os.path.join(outdir, 'occ_rates.csv'))

    for dim in marker_hashtags.keys():
        top_hashtags[dim] = (top_hashtags['subset_rate_occ_pro_{}'.format(dim)] - top_hashtags['subset_rate_occ_neg_{}'.format(dim)]) / top_hashtags['baseline_rate_occ']

    cols = ['index'] + list(marker_hashtags.keys())
    #cols.append('index')
    top_hashtags[cols].to_csv(os.path.join(outdir, 'polarities.csv'))

    # print(top_hashtags.columns)
    logger.info('Finish computing hashtag polarities')
    return top_hashtags


def compute_hashtag_stats(logger, tweets, data, tweet_ids, data_path, outdir, 
    n_hashtags, case_sensitive, marker_hashtags, 
    calculate_hashtag_polarities, calculate_user_polarities):
    logger.info('hello from compute hashtag stats')
    os.makedirs(outdir, exist_ok=True)
    top_hashtags = get_top_hashtags(logger, data, outdir, n_hashtags, case_sensitive)
    compute_hashtag_polarities(logger, data, top_hashtags, outdir, n_hashtags, marker_hashtags, case_sensitive)
    return

def get_hashtag_counts(user_df, case_sensitive):
    def get_hashtags(input_str):
        if type(input_str) != str:
            return []
        if not case_sensitive:
            input_str = input_str.lower()
        return [elem[9:-1].replace('_', '').replace('ー', '') for elem in re.findall("'text': '\w+'", input_str)]
    user_df['list_hashtags'] = user_df['entities/hashtags'].apply(get_hashtags)
    hashtag_counts = pd.Series(user_df['list_hashtags'].sum()).value_counts()
    return hashtag_counts


def compute_user_stats(logger, tweets, polarities, tweet_ids, data_path, outdir, n_hashtags, case_sensitive, marker_hashtags,
    calculate_hashtag_polarities, calculate_user_polarities):
    print(polarities.set_index('index'))
    for tweet_id, user_dict in tweets.items():
        for user_id, user_df in user_dict['user_ids'].items():
            print(user_id)
            print(user_df.shape)
            ht_counts = get_hashtag_counts(user_df, case_sensitive)
            print(polarities.join(pd.DataFrame(ht_counts)))
            # print(polarities.join(ht_counts))
            # print(get_hashtag_counts(user_df, case_sensitive))
    logger.info('hello from compute user stats')
    return

#!/usr/bin/env python

import sys
import json
import pandas as pd
import os
import logging
import pickle

sys.path.insert(0, 'src')

from etl import get_data
#from etl import get_data_pancea_tweets
from eda import generate_stats
from analysis import compute_hashtag_stats
from analysis import compute_user_stats
from utils import convert_notebook
from logging.handlers import RotatingFileHandler

def main(targets):
    '''
    Runs the main project pipeline logic, given the targets.
    targets must contain: 'data', 'analysis', 'model'. 
    
    `main` runs the targets in order of data=>analysis=>model.
    '''
    # Setup Logger
    logger = logging.getLogger('project_log')
    logger.setLevel(logging.DEBUG)
    fh = RotatingFileHandler('example.log', maxBytes=1000000, backupCount=0)
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.info('STARTING PROGRAM')

    if 'data' in targets or 'all' in targets:
        with open('config/data-params.json') as fh:
            data_cfg = json.load(fh)
        with open('config/twitter-api-keys.json') as fh:
            twitter_cfg = json.load(fh)
        get_data(logger, **data_cfg, **twitter_cfg)

    if 'analysis' in targets or 'all' in targets:
        with open('config/analysis-params.json') as fh:
            analysis_cfg = json.load(fh)

        # do hashtag stats
        if analysis_cfg['calculate_hashtag_polarities']:
            tweets = {}
            data = pd.read_csv(os.path.join(analysis_cfg['data_path'], 'data.csv')).drop(columns=['Unnamed: 0'])
            compute_hashtag_stats(logger, tweets, data, **analysis_cfg)

        # do user stats
        if analysis_cfg['calculate_user_polarities']:
            tweets = {}
            for tweet_id in analysis_cfg['tweet_ids']:
                path = os.path.join(analysis_cfg['data_path'], 'tweet_{}.csv'.format(tweet_id))
                tweet = pickle.load(open(path, 'rb'))
                tweets[tweet_id] = tweet
            
            for key, value in tweets.items():
                for user_id in list(value['user_ids'].keys()):
                    value['user_ids'][user_id] = pd.read_csv(os.path.join(analysis_cfg['data_path'], 'user_{}_tweets.csv'.format(user_id)))
            data = pd.read_csv(os.path.join(analysis_cfg['outdir'], 'polarities.csv')).drop(columns=['Unnamed: 0'])
            compute_user_stats(logger, tweets, data, **analysis_cfg)

        # execute notebook / convert to html
        try:
            convert_notebook('analysis', **analysis_cfg)
            logger.info('finished analysis target: wrote html file to {}'.format(os.path.join(analysis_cfg['outdir'], 'analysis.html')))
        except:
            logger.info('finished analysis but error in making target')


    if 'test' in targets:
        with open('config/analysis-params.json') as fh:
            analysis_cfg = json.load(fh)

        # do hashtag stats
        if analysis_cfg['calculate_hashtag_polarities']:
            tweets = {}
            data = pd.read_csv(os.path.join(analysis_cfg['data_path'], 'data.csv')) #.drop(columns=['Unnamed: 0'])
            compute_hashtag_stats(logger, tweets, data, **analysis_cfg)

        # do user stats
        if analysis_cfg['calculate_user_polarities']:
            tweets = {}
            for tweet_id in analysis_cfg['tweet_ids']:
                path = os.path.join(analysis_cfg['data_path'], 'tweet_{}.csv'.format(tweet_id))
                tweet = pickle.load(open(path, 'rb'))
                tweets[tweet_id] = tweet
            for key, value in tweets.items():
                for user_id in list(value['user_ids'].keys()):
                    value['user_ids'][user_id] = pd.read_csv(os.path.join(analysis_cfg['data_path'], 'user_{}_tweets.csv'.format(user_id)))
            data = pd.read_csv(os.path.join(analysis_cfg['outdir'], 'polarities.csv')).drop(columns=['Unnamed: 0'])
            compute_user_stats(logger, tweets, data, **analysis_cfg)

        # execute notebook / convert to html
        try:
            convert_notebook('analysis', **analysis_cfg)
            logger.info('finished analysis target: wrote html file to {}'.format(os.path.join(analysis_cfg['outdir'], 'analysis.html')))
        except:
            logger.info('finished analysis but error in making target')
    return


if __name__ == '__main__':
    # run via:
    # python main.py data model
    targets = sys.argv[1:]
    main(targets)

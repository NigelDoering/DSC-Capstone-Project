#!/usr/bin/env python

import sys
import json
import pandas as pd
import os
import logging

sys.path.insert(0, 'src')

from etl import get_data
from eda import generate_stats
from analysis import compute_stats
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
        logger.info("starting data target")
        with open('config/data-params.json') as fh:
            data_cfg = json.load(fh)
        data = get_data(logger, **data_cfg)
        # make the data target
        logger.info("finished data target")

    if 'eda' in targets or 'all' in targets:
        logger.info("starting eda target")
        with open('config/eda-params.json') as fh:
            eda_cfg = json.load(fh)
        data = pd.read_csv(os.path.join(eda_cfg["data_path"], 'data.csv'), usecols=['entities/hashtags', 'id', 'created_at', 'user/id'])
        logger.info("shape of dataframe is {}".format(data.shape))
        generate_stats(logger, data, **eda_cfg)

        # execute notebook / convert to html
        convert_notebook('eda', **eda_cfg)
        logger.info("finished eda target: wrote html file to {}".format(os.path.join(eda_cfg["outdir"], 'eda.html')))

    if 'analysis' in targets or 'all' in targets:
        logger.info("starting analysis target")
        with open('config/analysis-params.json') as fh:
            analysis_cfg = json.load(fh)

        data = pd.read_csv(os.path.join(analysis_cfg["data_path"], 'data.csv'), usecols=['entities/hashtags', 'id', 'created_at', 'user/id'])
        user_dfs = []
        for user_id in analysis_cfg['user_ids']:
            user_dfs.append(pd.read_csv(os.path.join(analysis_cfg["data_path"], 'user_{}_tweets.csv'.format(user_id))))
        tweet_user_dfss = []
        for tweet_id in analysis_cfg['tweet_ids']:
            tweet_info = pd.read_csv(os.path.join(analysis_cfg["data_path"], 'tweet_{}.csv'.format(tweet_id)), usecols=['cat', 'data'])
            tweet_info = tweet_info.set_index('cat')['data']
            user_ids = tweet_info['user_ids'][1:-1].replace(" ", "").split(',')
            logger.info(user_ids)
            tweet_user_dfs = []
            for user in user_ids:
                tweet_user_dfs.append(pd.read_csv(os.path.join(analysis_cfg["data_path"], 'user_{}_tweets.csv'.format(user))))
            tweet_user_dfss.append(tweet_user_dfs)
        top_hashtags = pd.read_csv(os.path.join(analysis_cfg["outdir"], 'top_hashtags.csv'), index_col=0)
        compute_stats(logger, data, top_hashtags, user_dfs, tweet_user_dfss, **analysis_cfg)

        # execute notebook / convert to html
        convert_notebook('analysis', **analysis_cfg)
        logger.info('finished analysis target: wrote html file to {}'.format(os.path.join(analysis_cfg['outdir'], 'analysis.html')))

    if 'test' in targets:
        logger.info("starting test target")
        # EDA
        logger.info("starting eda target")
        with open('config/eda-params.json') as fh:
            eda_cfg = json.load(fh)
        data = pd.read_csv('test/testdata/tweets.csv', usecols=['entities/hashtags', 'id', 'created_at', 'user/id'])
        logger.info("shape of dataframe is {}".format(data.shape))
        generate_stats(logger, data, **eda_cfg)

        # execute notebook / convert to html
        convert_notebook('eda', **eda_cfg)
        logger.info("finished eda target: wrote html file to {}".format(os.path.join(eda_cfg["outdir"], 'eda.html')))

        # Analysis
        logger.info("starting analysis target")
        with open('config/analysis-params.json') as fh:
            analysis_cfg = json.load(fh)
        data = pd.read_csv('test/testdata/tweets.csv', usecols=['entities/hashtags', 'id', 'created_at', 'user/id'])
        user_dfs = []
        for user_id in analysis_cfg['user_ids']:
            user_dfs.append(pd.read_csv(os.path.join('test/testdata', 'user_{}_tweets.csv'.format(user_id))))
        tweet_user_dfss = []
        for tweet_id in analysis_cfg['tweet_ids']:
            tweet_info = pd.read_csv(os.path.join('test/testdata', 'tweet_{}.csv'.format(tweet_id)), usecols=['cat', 'data'])
            tweet_info = tweet_info.set_index('cat')['data']
            user_ids = tweet_info['user_ids'][1:-1].replace(" ", "").split(',')
            logger.info(user_ids)
            tweet_user_dfs = []
            for user in user_ids:
                tweet_user_dfs.append(pd.read_csv(os.path.join('test/testdata', 'user_{}_tweets.csv'.format(user.replace("'","")))))
            tweet_user_dfss.append(tweet_user_dfs)
        top_hashtags = pd.read_csv(os.path.join(analysis_cfg["outdir"], 'top_hashtags.csv'), index_col=0)
        compute_stats(logger, data, top_hashtags, user_dfs, tweet_user_dfss, **analysis_cfg)

        # execute notebook / convert to html
        convert_notebook('analysis', **analysis_cfg)
        logger.info('finished analysis target: wrote html file to {}'.format(os.path.join(analysis_cfg['outdir'], 'analysis.html')))
        logger.info("finished test target")



    # if 'analysis' in targets:
    #     with open('config/analysis-params.json') as fh:
    #         analysis_cfg = json.load(fh)

    #     # make the data target
    #     compute_aggregates(data, **analysis_cfg)

    # if 'model' in targets:
    #     with open('config/model-params.json') as fh:
    #         model_cfg = json.load(fh)

    #     # make the data target
    #     train(data, **model_cfg)

    return


if __name__ == '__main__':
    # run via:
    # python main.py data model
    targets = sys.argv[1:]
    main(targets)

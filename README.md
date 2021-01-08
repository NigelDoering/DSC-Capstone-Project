# DSC180A-Replication1

## Data
### Info
* The data being used here is COVID-19 Tweets collected by Pancea Lab (http://www.panacealab.org/covid19/).
### Preqrequisites
* Ensure libraries are installed. (pandas, requests, os, gzip, shutil, json, flatten).
* Download repo: https://github.com/thepanacealab/covid19_twitter.
* Docker container id: tmpankaj/example-docker
### How to Run
* All parameters are of type str unless specified otherwise
* run 'python run.py all' in root directory of repo to run data, eda, and analysis
#### Test
* Go inside docker container
* Parameters are already set for testing
* run 'python run.py test' in root directory of repo
* this will run eda and analysis on test data and output the eda.html and analysis.html in /test/visualizations
#### Data
* Go inside docker container
* Set data parameters in config/data-params.json.
    * consumer_key, consumer_secret_key, access_token, access_token_secret, bearer_token: all Twitter API credentials.
    * repo_path: path to directory that contains Pancea Lab GitHub repo
    * start_date, end_date: dates to collect Pancea Lab tweets from (leave both as "" to skip this part) e.g. "2020-06-20"
    * output_path: path to directory to write data to
    * frac (float): fraction of Pancea lab tweets to collect per day
    * user_ids (list of str): Twitter User IDs to collect tweets from for the analysis portion
    * tweet_ids (list of str): Twitter Tweet IDs to collect users who retweeted for the analysis portion
* run 'python run.py data' in root directory of repo
* This will only collect the data
#### EDA
* Set eda paramaters in config/eda-params.json.
    * data_path: path to directory that contains data (should be same directory as data-params output path)
    * outdir: path to directory to output visualizations and targets
    * n_hashtags (int): this is the number of top hashtags to find
    * case_sensitive (bool): whether or not to be case sensitive with hashtags
    * hashtag (list of str): hashtags to make a visualization for the number of times the hashtag was used each day in the data
* run 'python run.py eda' in root directory of repo
* This will create an eda.html file with all the results inside your outdir directory 
#### Analysis
* Set analysis parameters in config/analysis-params.json.
    * data_path: path to directory that contains data (should be same directory as data-params output path)
    * outdir: path to directory to output visualizations and targets
    * n_hashtags (int): number of top hashtags to use in calculating user polarity
    * case_sensitive (bool): whether or not to be case sensitive with hashtags
    * marker_hashtags (list of str): hashtags that we are fairly confident are associated with conspiracy (will be used to calculate polarities)
    * user_ids (list of str): user id's to calculate polarity
    * tweet_ids (list of str): tweet id's to use to generate histogram of user's who retweeted polarities
* run 'python run.py analysis' in root directory of repo
* This will create an analysis.html file with all the results inside your outdir directory 

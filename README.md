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
    * output_path: path to directory to write data to
    * exclude_replies (bool): if true, excludes replies for each of the users that retweeted the major tweets being analyzed
    * include_rts (bool): if true, includes retweets for each of the users that retweeted the major tweets being analyzed
    * max_recent_tweets (int): maximum number of recent tweets to get from each of the users that retweeted the major tweets being analyzed
    * tweets_ids (list of str): major Tweet IDs to analyze
* run 'python run.py data' in root directory of repo
* This will only collect the data
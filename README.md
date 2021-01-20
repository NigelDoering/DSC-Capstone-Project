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
* Set twitter API Keys in config/twitter-api-keys.json
#### Major Tweets Data 
* Go inside docker container
* Set major tweets data parameters in config/data-params-major-tweets.json.
    * output_path: path to directory to write data to
    * exclude_replies (bool): if true, excludes replies for each of the users that retweeted the major tweets being analyzed
    * include_rts (bool): if true, includes retweets for each of the users that retweeted the major tweets being analyzed
    * max_recent_tweets (int): maximum number of recent tweets to get from each of the users that retweeted the major tweets being analyzed
    * tweets_ids (list of str): major Tweet IDs to analyze
* Set Pancea Lab tweets data parameters in config/data-params-pancea-tweets.json.
    * repo_path: path to directory that contains GitHub repo previously downloaded. (Make sure the directory is called 'covid19_twitter')
    * start_date, end_date: dates to collect Pancea Lab tweets from (leave both as "" to skip this part) e.g. "2020-06-20"
    * clean (bool): True uses the cleaned set which does not include retweets
    * output_path: path to directory to write data to
    * frac (float): uses only this fraction of the tweets
* run 'python run.py data-major' and/or 'python run.py data-pancea' in root directory of repo
* This will only collect the data
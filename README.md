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
#### Data 
* Go inside docker container
* Set Pancea Lab tweets data parameters in config/data-params.json.
    * pancea_tweets (bool): Toggle on/off to collect this data. (the other parameters will be ignored if this is false)
    * repo_path: path to directory that contains GitHub repo previously downloaded. (Make sure the directory is called 'covid19_twitter')
    * start_date, end_date: dates to collect Pancea Lab tweets from (leave both as "" to skip this part) e.g. "2020-06-20"
    * clean (bool): True uses the cleaned set which does not include retweets
    * output_path: path to directory to write data to
    * frac (float): uses only this fraction of the tweets
* Set major tweets data parameters in config/data-params.json.
    * major_tweets (bool): Toggle on/off to collect this data. (the other parameters will be ignored if this is false)
    * output_path: path to directory to write data to
    * exclude_replies (bool): if true, excludes replies for each of the users that retweeted the major tweets being analyzed
    * include_rts (bool): if true, includes retweets for each of the users that retweeted the major tweets being analyzed
    * max_recent_tweets (int): maximum number of recent tweets to get from each of the users that retweeted the major tweets being analyzed
    * tweets_ids (list of str): major Tweet IDs to analyze
* run 'python run.py data' in root directory of repo
* This will only collect the data
#### Analysis
* Go inside docker container
* Set Hashtag polarity parameters in config/analysis-params.json.
    * calculate_hashtag_polarities (bool): Toggle on/off to calculate hashtag polarities (the other parameters will be ignored if this is false)
    * data_path: path to directory where the Pancea Lab tweets data is
    * outdir: path to directory where to output visualizations and analysis
    * n_hashtags: number of top hashtags to use
    * case_sensitive (bool): If true, case sensitive on hashtags. Otherwise, it is not.
    * marker_hashtags (dict): Each key in the dictionary should be a dimension. Each value should be a list containing 2 elements, each being another list.
    The first list should be the marker hashtags for the positive direction of the dimension and the second list should be the negative direction of the dimension.
    For example,  "marker_hashtags": {"science": [["stayhome"], ["plandemic"]],
        "political": [["chinavirus"], ["trumpvirus"]],
        "moderacy": [["trumpvirus", "chinavirus"], ["pandemic", "lockdown"]]}.
* Set User polaritiy parameters in config/analysis-params.json.
    * calculate_user_polarities (bool): Toggle on/off to calcualte user polarities (the other parameters will be ignored if this is false). Keep in mind this analysis needs outputs from hashtag polarities.
    * tweet_ids (list): List of tweet IDs in which to take the users who retweeted and calculate the polarities. 
* run 'python run.py analysis' in root directory of repo (Keep in mind this is dependent on having already collected data)
#### Test
* run 'python run.py test' in root directory of repo
* Look in /test/ for results

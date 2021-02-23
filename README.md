# Data Science Capstone Project

## Data
### Info
* The data being used here is Tweets from various news sources.
### Preqrequisites
* Ensure libraries are installed. (pandas, requests, os, gzip, shutil, json, flatten).
* Download repo: https://github.com/thepanacealab/covid19_twitter.
* Docker container id: tmpankaj/example-docker
### How to Run
* All parameters are of type str unless specified otherwise
* Set twitter API Keys in config/twitter-api-keys.json
#### Data 
* Go inside docker container
* Make sure directories exist
* Add .txt files with Tweet IDs from https://tweetsets.library.gwu.edu/ to some directory where preprocessed data will be stored. (E.g. cnn.txt in /data/preprocessed directory)
* Use this hydrator https://github.com/DocNow/hydrator to hydrate these tweets and make sure there is a .csv file in the same directory (E.g. cnn.csv in /data/preprocessed)
* Set data parameters in config/data-params.json
   * preprocessed_data_path: path to directory of preprocessed data
   * output_data_path: path to directory to output .csv file for training data
   * dims (list of str): list of the names of the dimensions that polarities will be eventually calculated on (E.g. ["moderacy", "misinformation"])
   * labels (dict): dictionary with the keys including the news sources and each value being a list with a 0/1 for each dimension (E.g. {"cnn": [0, 1], "fox": [1, 0]})
* run 'python run.py data' in root directory of repo
* This will only collect the data


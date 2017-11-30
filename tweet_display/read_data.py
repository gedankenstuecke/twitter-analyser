from timezonefinder import TimezoneFinder
import tempfile
import zipfile
import json
import datetime
import pytz

import io
import pandas as pd
import requests


#tzwhere_ = tzwhere.tzwhere()
tzf = TimezoneFinder()


### READ JSON FILES FROM TWITTER ARCHIVE!

def check_hashtag(single_tweet):
    '''check whether tweet has any hashtags'''
    return len(single_tweet['entities']['hashtags']) > 0

def check_media(single_tweet):
    '''check whether tweet has any media attached'''
    return len(single_tweet['entities']['media' ]) > 0

def check_url(single_tweet):
    '''check whether tweet has any urls attached'''
    return len(single_tweet['entities']['urls']) > 0

def check_retweet(single_tweet):
    '''
    check whether tweet is a RT. If yes:
    return name & user name of the RT'd user.
    otherwise just return nones
    '''
    if 'retweeted_status' in single_tweet.keys():
        return (single_tweet['retweeted_status']['user']['screen_name'],
                single_tweet['retweeted_status']['user']['name'])
    else:
        return (None,None)

def check_coordinates(single_tweet):
    '''
    check whether tweet has coordinates attached.
    if yes return the coordinates
    otherwise just return nones
    '''
    if 'coordinates' in single_tweet['geo'].keys():
        return (single_tweet['geo']['coordinates'][0],
                single_tweet['geo']['coordinates'][1])
    else:
        return (None,None)

def check_reply_to(single_tweet):
    '''
    check whether tweet is a reply. If yes:
    return name & user name of the user that's replied to.
    otherwise just return nones
    '''
    if 'in_reply_to_screen_name' in single_tweet.keys():
        name = None
        for user in single_tweet['entities']['user_mentions']:
            if user['screen_name'] == single_tweet['in_reply_to_screen_name']:
                name = user['name']
                break
        return (single_tweet['in_reply_to_screen_name'],name)
    else:
        return (None,None)

def convert_time(coordinates,time_utc):
    '''
    Does this tweet have a geo location? if yes
    we can easily convert the UTC timestamp to true local time!
    otherwise return nones
    '''
    if coordinates[0] and coordinates[1]:
        timezone_str = tzf.timezone_at(coordinates[0],coordinates[1])
        if timezone_str:
            timezone = pytz.timezone(timezone_str)
            time_obj_local = datetime.datetime.astimezone(time_utc,timezone)
            return time_obj_local

def create_dataframe(tweets):
    '''
    create a pandas dataframe from our tweet jsons
    '''

    # initalize empty lists
    utc_time = []
    longitude = []
    latitude = []
    local_time = []
    hashtag = []
    media = []
    url = []
    retweet_user_name = []
    retweet_name = []
    reply_user_name = []
    reply_name = []
    text = []
    # iterate over all tweets and extract data
    for single_tweet in tweets:
        utc_time.append(datetime.datetime.strptime(single_tweet['created_at'],'%Y-%m-%d %H:%M:%S %z'))
        coordinates = check_coordinates(single_tweet)
        latitude.append(coordinates[0])
        longitude.append(coordinates[1])
        local_time.append(convert_time(coordinates,datetime.datetime.strptime(single_tweet['created_at'],'%Y-%m-%d %H:%M:%S %z')))
        hashtag.append(check_hashtag(single_tweet))
        media.append(check_media(single_tweet))
        url.append(check_url(single_tweet))
        retweet = check_retweet(single_tweet)
        retweet_user_name.append(retweet[0])
        retweet_name.append(retweet[1])
        reply = check_reply_to(single_tweet)
        reply_user_name.append(reply[0])
        reply_name.append(reply[1])
        text.append(single_tweet['text'])
    # convert the whole shebang into a pandas dataframe
    dataframe = pd.DataFrame(data= {
                    'utc_time' : utc_time,
                    'local_time' : local_time,
                    'latitude' : latitude,
                    'longitude' : longitude,
                    'hashtag' : hashtag,
                    'media' : media,
                    'url' : url,
                    'retweet_user_name' : retweet_user_name,
                    'retweet_name' : retweet_name,
                    'reply_user_name' : reply_user_name,
                    'reply_name' : reply_name,
                    'text' : text
    })
    return dataframe

def read_files(zip_url):
    tf = tempfile.NamedTemporaryFile()
    print('downloading files')
    tf.write(requests.get(zip_url).content)
    zf = zipfile.ZipFile(tf.name)
    print('reading index')
    with zf.open('data/js/tweet_index.js','r') as f:
        f  = io.TextIOWrapper(f)
        d = f.readlines()[1:]
        d = "[{" + "".join(d)
        json_files = json.loads(d)
    data_frames = []
    print('iterate over individual files')
    for single_file in json_files:
        with zf.open(single_file['file_name']) as f:
            f  = io.TextIOWrapper(f)
            d = f.readlines()[1:]
            d = "".join(d)
            tweets = json.loads(d)
            df_tweets = create_dataframe(tweets)
            data_frames.append(df_tweets)
    return data_frames

def create_main_dataframe(zip_url='http://ruleofthirds.de/test_archive.zip'):
    print('reading files')
    dataframes = read_files(zip_url)
    print('concatenating...')
    dataframe = pd.concat(dataframes)
    dataframe = dataframe.sort_values('utc_time',ascending=False)
    dataframe = dataframe.set_index('utc_time')
    dataframe = dataframe.replace(to_replace={
                                    'url': {False: None},
                                    'hashtag': {False: None},
                                    'media': {False: None}
                                    })
    return dataframe

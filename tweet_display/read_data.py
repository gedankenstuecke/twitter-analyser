from timezonefinder import TimezoneFinder
import tempfile
import zipfile
import json
import datetime
import pytz
import ijson
import io
import pandas as pd
import requests


# tzwhere_ = tzwhere.tzwhere()
tzf = TimezoneFinder()


# READ JSON FILES FROM TWITTER ARCHIVE!

def check_hashtag(single_tweet):
    '''check whether tweet has any hashtags'''
    return len(single_tweet['entities']['hashtags']) > 0


def check_media(single_tweet):
    '''check whether tweet has any media attached'''
    if 'media' in single_tweet['entities'].keys():
        return len(single_tweet['entities']['media']) > 0
    else:
        return False


def check_url(single_tweet):
    '''check whether tweet has any urls attached'''
    return len(single_tweet['entities']['urls']) > 0


def check_retweet(single_tweet):
    '''
    check whether tweet is a RT. If yes:
    return name & user name of the RT'd user.
    otherwise just return nones
    '''
    if single_tweet['full_text'].startswith("RT @"):
        if len(single_tweet['entities']['user_mentions']) > 0:
            return (
                single_tweet['entities']['user_mentions'][0]['screen_name'],
                single_tweet['entities']['user_mentions'][0]['name'],)
    if 'retweeted_status' in single_tweet.keys():
        return (single_tweet['retweeted_status']['user']['screen_name'],
                single_tweet['retweeted_status']['user']['name'])
    return (None, None)


def check_coordinates(single_tweet):
    '''
    check whether tweet has coordinates attached.
    if yes return the coordinates
    otherwise just return nones
    '''
    if 'geo' in single_tweet.keys():
        if 'coordinates' in single_tweet['geo'].keys():
            return (float(single_tweet['geo']['coordinates'][0]),
                    float(single_tweet['geo']['coordinates'][1]))
        else:
            return (None, None)
    else:
        return (None, None)


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
        return (single_tweet['in_reply_to_screen_name'], name)
    else:
        return (None, None)


def convert_time(coordinates, time_utc):
    '''
    Does this tweet have a geo location? if yes
    we can easily convert the UTC timestamp to true local time!
    otherwise return nones
    '''
    if coordinates[0] and coordinates[1]:
        timezone_str = tzf.timezone_at(lat=coordinates[0], lng=coordinates[1])
        if timezone_str:
            timezone = pytz.timezone(timezone_str)
            time_obj_local = datetime.datetime.astimezone(time_utc, timezone)
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
        try:
            utc_time.append(
                datetime.datetime.strptime(
                    single_tweet['created_at'],
                    '%a %b %d %H:%M:%S %z %Y'))
        except ValueError:
            utc_time.append(
                datetime.datetime.strptime(
                    single_tweet['created_at'],
                    '%Y-%m-%d %H:%M:%S %z'))
        coordinates = check_coordinates(single_tweet)
        latitude.append(coordinates[0])
        longitude.append(coordinates[1])
        try:
            creation_time = datetime.datetime.strptime(
                    single_tweet['created_at'],
                    '%a %b %d %H:%M:%S %z %Y')
        except ValueError:
            creation_time = datetime.datetime.strptime(single_tweet['created_at'],
                                                       '%Y-%m-%d %H:%M:%S %z')
        converted_time = convert_time(coordinates, creation_time)
        local_time.append(converted_time)
        hashtag.append(check_hashtag(single_tweet))
        media.append(check_media(single_tweet))
        url.append(check_url(single_tweet))
        retweet = check_retweet(single_tweet)
        retweet_user_name.append(retweet[0])
        retweet_name.append(retweet[1])
        reply = check_reply_to(single_tweet)
        reply_user_name.append(reply[0])
        reply_name.append(reply[1])
        text.append(single_tweet['full_text'])
    # convert the whole shebang into a pandas dataframe
    dataframe = pd.DataFrame(data={
                            'utc_time': utc_time,
                            'local_time': local_time,
                            'latitude': latitude,
                            'longitude': longitude,
                            'hashtag': hashtag,
                            'media': media,
                            'url': url,
                            'retweet_user_name': retweet_user_name,
                            'retweet_name': retweet_name,
                            'reply_user_name': reply_user_name,
                            'reply_name': reply_name,
                            'text': text,
    })
    return dataframe


def fetch_zip_file(zip_url):
    tf = tempfile.NamedTemporaryFile()
    print('downloading files')
    tf.write(requests.get(zip_url).content)
    tf.flush()
    if zipfile.is_zipfile(tf.name):
        return (zipfile.ZipFile(tf.name), 'zipped')
    else:
        return (open(tf.name, 'r'), 'json')


def read_old_zip_archive(zf):
    with zf.open('data/js/tweet_index.js', 'r') as f:
        f = io.TextIOWrapper(f)
        d = f.readlines()[1:]
        d = "[{" + "".join(d)
        json_files = json.loads(d)
    data_frames = []
    print('iterate over individual files')
    for single_file in json_files:
        print('read ' + single_file['file_name'])
        with zf.open(single_file['file_name']) as f:
            f = io.TextIOWrapper(f)
            d = f.readlines()[1:]
            d = "".join(d)
            tweets = json.loads(d)
            df_tweets = create_dataframe(tweets)
            data_frames.append(df_tweets)
    return data_frames


def read_files(zf, filetype):
    if filetype == 'zipped':
        if 'data/js/tweet_index.js' in zf.namelist():
            print('reading index')
            data_frames = read_old_zip_archive(zf)
            return data_frames
        elif 'tweet.js' in zf.namelist():
            with zf.open('tweet.js') as f:
                f = io.TextIOWrapper(f)
                tweet_string = f.readlines()
                tweet_string = "".join([i.strip() for i in tweet_string])
                tweet_string = tweet_string[25:]

    elif filetype == 'json':
        tweet_string = zf.readlines()
        tweet_string = "".join([i.strip() for i in tweet_string])
        tweet_string = tweet_string[25:]
    correct_json = tempfile.NamedTemporaryFile(mode='w')
    correct_json.write(tweet_string)
    correct_json.flush()
    tweets = ijson.items(open(correct_json.name, 'r'), 'item')
    data_frame = create_dataframe(tweets)
    return [data_frame]


def create_main_dataframe(zip_url='http://ruleofthirds.de/test_archive.zip'):
    if zip_url.startswith('http'):
        print('reading zip file from web')
        zip_file, filetype = fetch_zip_file(zip_url)
    elif os.path.isfile(zip_url):
        print('reading zip file from disk')
        zip_file = zipfile.ZipFile(zip_url)
        filetype = 'zipped'
    else:
        raise ValueError('zip_url is not an URL nor a file in disk')

    dataframes = read_files(zip_file, filetype)
    print('concatenating...')
    dataframe = pd.concat(dataframes)
    dataframe = dataframe.sort_values('utc_time', ascending=False)
    dataframe = dataframe.set_index('utc_time')
    dataframe = dataframe.replace(to_replace={
                                    'url': {False: None},
                                    'hashtag': {False: None},
                                    'media': {False: None}
                                    })
    return dataframe

import pandas as pd
import gender_guesser.detector as gender
import geojson
gender_guesser = gender.Detector(case_sensitive=False)

def predict_gender(dataframe,column_name,rolling_frame='180d'):
    '''
    take full dataframe w/ tweets and extract
    gender for a name-column where applicable
    returns two-column df w/ timestamp & gender
    '''
    splitter = lambda x: x.split()[0]
    gender_column = dataframe.loc[dataframe[column_name].notnull()][column_name].apply(
        splitter).apply(
        gender_guesser.get_gender)

    gender_dataframe = pd.DataFrame(data = {
                    'time' : list(gender_column.index),
                    'gender' : list(gender_column)
                    })

    gender_dataframe = gender_dataframe.set_index('time')
    gender_dataframe_tab = gender_dataframe.groupby([gender_dataframe.index.date,gender_dataframe['gender']]).size().reset_index()
    gender_dataframe_tab['date'] = gender_dataframe_tab['level_0']
    gender_dataframe_tab['count'] = gender_dataframe_tab[0]
    gender_dataframe_tab = gender_dataframe_tab.drop([0,'level_0'],axis=1)
    gender_dataframe_tab = gender_dataframe_tab.set_index('date')
    gender_dataframe_tab.index = pd.to_datetime(gender_dataframe_tab.index)
    gdf_pivot = gender_dataframe_tab.pivot(columns='gender', values='count')
    gdf_pivot = gdf_pivot.rolling(rolling_frame).mean()
    gdf_pivot = gdf_pivot.reset_index()
    gdf_pivot['date'] = gdf_pivot['date'].astype(str)
    gdf_pivot = gdf_pivot.drop(['mostly_male','mostly_female','andy','unknown'],axis=1)
    return gdf_pivot

def create_hourly_stats(dataframe):
    get_hour = lambda x: x.hour
    get_weekday = lambda x: x.weekday()

    local_times = dataframe.copy()
    local_times = local_times.loc[dataframe['local_time'].notnull()]

    local_times['weekday'] = local_times['local_time'].apply(get_weekday)
    local_times['hour'] = local_times['local_time'].apply(get_hour)


    local_times = local_times.replace(to_replace={'weekday':
                                                    {0:'Weekday',
                                                     1:'Weekday',
                                                     2:'Weekday',
                                                     3:'Weekday',
                                                     4:'Weekday',
                                                     5:'Weekend',
                                                     6:'Weekend',
                                                    }
                                       })

    local_times = local_times.groupby([local_times['hour'],local_times['weekday']]).size().reset_index()
    local_times['values'] = local_times[0]
    local_times = local_times.set_index(local_times['hour'])

    local_times = local_times.pivot(columns='weekday', values='values').reset_index()
    local_times['Weekday'] = local_times['Weekday'] / 5
    local_times['Weekend'] = local_times['Weekend'] / 2

    return local_times.reset_index()



def create_tweet_types(dataframe):
    dataframe_grouped = dataframe.groupby(dataframe.index.date).count()
    dataframe_grouped.index = pd.to_datetime(dataframe_grouped.index)

    dataframe_mean_week = dataframe_grouped.rolling('180d').mean()
    dataframe_mean_week['p_url'] = (dataframe_mean_week['url'] / dataframe_mean_week['text']) * 100
    dataframe_mean_week['p_media'] = (dataframe_mean_week['media'] / dataframe_mean_week['text']) * 100
    dataframe_mean_week['p_reply'] = (dataframe_mean_week['reply_name'] / dataframe_mean_week['text']) * 100
    dataframe_mean_week['p_rt'] = (dataframe_mean_week['retweet_name'] / dataframe_mean_week['text']) * 100
    dataframe_mean_week['p_hash'] = (dataframe_mean_week['hashtag'] / dataframe_mean_week['text']) * 100
    dataframe_mean_week['p_other'] = 100 - (dataframe_mean_week['p_reply'] + dataframe_mean_week['p_rt'])

    dataframe_mean_week = dataframe_mean_week.reset_index()
    dataframe_mean_week['date'] = dataframe_mean_week['index'].astype(str)
    dataframe_mean_week = dataframe_mean_week.drop(['reply_user_name',
                                                    'retweet_user_name',
                                                    'latitude',
                                                    'longitude',
                                                    'local_time',
                                                    'url',
                                                    'media',
                                                    'reply_name',
                                                    'retweet_name',
                                                    'hashtag',
                                                    'index',
                                                   ],
                                                   axis=1)

    return dataframe_mean_week.reset_index()


def create_top_replies(dataframe):
    top_replies = dataframe[dataframe['reply_user_name'].isin(list(dataframe['reply_user_name'].value_counts()[:5].reset_index()['index']))]
    top_replies = top_replies.reset_index()[['reply_user_name','utc_time']]
    top_replies['utc_time'] = top_replies['utc_time'].dt.date
    top_replies = top_replies.groupby(["utc_time", "reply_user_name"]).size()
    top_replies = top_replies.reset_index()
    top_replies['date'] = top_replies['utc_time'].astype(str)
    top_replies['value'] = top_replies[0]
    top_replies = top_replies.drop([0,'utc_time'],axis=1)
    top_replies['date'] = pd.to_datetime(top_replies['date'])
    top_replies = top_replies.groupby(['reply_user_name', pd.Grouper(key='date', freq='QS')])['value'].sum().reset_index().sort_values('date')
    top_replies['date'] = top_replies['date'].astype(str)
    return top_replies.reset_index().pivot(index='date', columns='reply_user_name', values='value').fillna(value=0).reset_index()

def create_heatmap(dataframe):
    return dataframe[dataframe['latitude'].notnull()][['latitude','longitude']]

def create_timeline(dataframe):
    timeline = dataframe[dataframe['latitude'].notnull()][['latitude','longitude']]
    timeline['start'] = timeline.index.date
    timeline['end'] = pd.Series(index=timeline.index).tshift(periods=21, freq='D').index.date
    features = []
    timeline.apply(lambda X: features.append(
        geojson.Feature(geometry=geojson.Point((float(X["longitude"]),
                                                float(X["latitude"]),)),
                        properties=dict(start=str(X["start"]),
                                    end=str(X["end"])))
                                            )
                , axis=1)

    return geojson.dumps(geojson.FeatureCollection(features))

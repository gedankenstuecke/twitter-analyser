import pandas as pd
import gender_guesser.detector as gender
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

    return local_times.pivot(columns='weekday', values='values').reset_index()

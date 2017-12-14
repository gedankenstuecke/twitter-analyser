from __future__ import absolute_import, unicode_literals
from celery import shared_task
from .models import Graph
from users.models import OpenHumansMember
from .helper import get_file_url
from .read_data import create_main_dataframe
from .analyse_data import predict_gender, create_hourly_stats
from .analyse_data import create_tweet_types, create_top_replies
from .analyse_data import create_heatmap, create_timeline, create_overall

# GENERATE JSON FOR GRAPHING ON THE WEB

# DUMP JSON FOR GRAPHING


def write_graph(dataframe, oh_user, graph_type, graph_desc,
                double_precision=2, orient='records'):
    json_object = dataframe.to_json(orient=orient)
    try:
        graph = Graph.objects.create(open_humans_member=oh_user)
        graph.graph_type = graph_type
        graph.graph_description = graph_desc
        graph.graph_data = str(json_object)
        graph.save()
    except Exception as e:
        graph.delete()


def write_json(json_object, oh_user, graph_type, graph_desc):
    try:
        graph = Graph.objects.create(open_humans_member=oh_user)
        graph.graph_type = graph_type
        graph.graph_description = graph_desc
        graph.graph_data = json_object
        graph.save()
    except Exception as e:
        graph.delete()


def delete_old_data(oh_user_id):
    graphs = Graph.objects.filter(open_humans_member__oh_id=oh_user_id)
    for graph in graphs:
        graph.delete()


@shared_task
def xsum(numbers):
    return sum(numbers)


@shared_task
def import_data(oh_user_id):
    url = get_file_url(oh_user_id)

    # NOTE: Might want to handle this more gracefully, e.g. prompt file upload.
    if not url:
        raise ValueError('No file found in Open Humans.')

    oh_user = OpenHumansMember.objects.get(oh_id=oh_user_id)
    delete_old_data(oh_user_id)
    dataframe = create_main_dataframe(url)
    retweet_gender = predict_gender(dataframe, 'retweet_name', '180d')
    write_graph(retweet_gender, oh_user, 'gender_rt', 'retweets by gender')
    reply_gender = predict_gender(dataframe, 'reply_name', '180d')
    write_graph(reply_gender, oh_user, 'gender_reply', 'replies by gender')
    hourly_stats = create_hourly_stats(dataframe)
    write_graph(hourly_stats, oh_user, 'hourly_tweets', 'tweets per hour')
    tweet_types = create_tweet_types(dataframe)
    write_graph(tweet_types, oh_user, 'tweet_types', 'tweet types over time')
    top_replies = create_top_replies(dataframe)
    write_graph(top_replies, oh_user, 'top_replies',
                'top users you replied to over time')
    heatmap = create_heatmap(dataframe)
    write_graph(heatmap, oh_user, 'heatmap',
                'heatmap of tweet geolocation', orient='values')
    timeline = create_timeline(dataframe)
    write_json(timeline, oh_user, 'timeline',
               'geojson to animate timeline')
    overall_tweets = create_overall(dataframe)
    write_graph(overall_tweets, oh_user, 'overall_tweets',
                'all tweets over time')

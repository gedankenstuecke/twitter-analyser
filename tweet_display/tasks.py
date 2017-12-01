from __future__ import absolute_import, unicode_literals
from celery import shared_task
from .models import Graph
import json

from .read_data import create_main_dataframe
from .analyse_data import predict_gender, create_hourly_stats
from .analyse_data import create_tweet_types, create_top_replies
from .analyse_data import create_heatmap, create_timeline

### GENERATE JSON FOR GRAPHING ON THE WEB

### DUMP JSON FOR GRAPHING
def write_graph(dataframe, graph_type, graph_desc,double_precision=2,orient='records'):
    json_object = dataframe.to_json(orient=orient)
    graph = Graph.objects.create()
    try:
        graph.graph_type = graph_type
        graph.graph_description = graph_desc
        graph.graph_data = str(json_object)
        graph.save()
    except:
        graph.delete()

def write_json(json_object,graph_type,graph_desc):
    graph = Graph.objects.create()
    try:
        graph.graph_type = graph_type
        graph.graph_description = graph_desc
        graph.graph_data = json_object
        graph.save()
    except:
        graph.delete()

@shared_task
def xsum(numbers):
    return sum(numbers)

@shared_task
def import_data(url='http://ruleofthirds.de/test_archive.zip'):
    dataframe = create_main_dataframe(url)
    retweet_gender = predict_gender(dataframe,'retweet_name','180d')
    write_graph(retweet_gender,'gender_rt','retweets by gender')
    reply_gender = predict_gender(dataframe,'reply_name','180d')
    write_graph(reply_gender,'gender_reply','replies by gender')
    hourly_stats = create_hourly_stats(dataframe)
    write_graph(hourly_stats,'hourly_tweets','tweets per hour')
    tweet_types = create_tweet_types(dataframe)
    write_graph(tweet_types,'tweet_types','tweet types over time')
    top_replies = create_top_replies(dataframe)
    write_graph(top_replies,'top_replies','top users you replied to over time')
    heatmap = create_heatmap(dataframe)
    write_graph(heatmap,'heatmap','heatmap of tweet geolocation',orient='values')
    timeline = create_timeline(dataframe)
    write_json(timeline,'timeline','geojson to animate timeline')

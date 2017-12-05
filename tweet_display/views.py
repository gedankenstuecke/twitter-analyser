from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render

from .models import Graph

# Create your views here.
def index(request):
    context = {}
    return render(request, 'tweet_display/index.html', context)

def gender_rt(request):
    graph = Graph.objects.filter(graph_type__exact='gender_rt')[0]
    return HttpResponse(graph.graph_data, content_type='application/json')

def gender_reply(request):
    graph = Graph.objects.filter(graph_type__exact='gender_reply')[0]
    return HttpResponse(graph.graph_data, content_type='application/json')


def hourly_tweets(request):
    graph = Graph.objects.filter(graph_type__exact='hourly_tweets')[0]
    return HttpResponse(graph.graph_data, content_type='application/json')

def tweet_types(request):
    graph = Graph.objects.filter(graph_type__exact='tweet_types')[0]
    return HttpResponse(graph.graph_data, content_type='application/json')

def top_replies(request):
    graph = Graph.objects.filter(graph_type__exact='top_replies')[0]
    return HttpResponse(graph.graph_data, content_type='application/json')

def heatmap(request):
    graph = Graph.objects.filter(graph_type__exact='heatmap')[0]
    return HttpResponse(graph.graph_data, content_type='application/json')

def timeline(request):
    graph = Graph.objects.filter(graph_type__exact='timeline')[0]
    return HttpResponse(graph.graph_data, content_type='application/json')

def overall_tweets(request):
    graph = Graph.objects.filter(graph_type__exact='overall_tweets')[0]
    return HttpResponse(graph.graph_data, content_type='application/json')

def location(request):
    context = {}
    return render(request, 'tweet_display/location.html', context)

def interactions(request):
    context = {}
    return render(request, 'tweet_display/interactions.html', context)

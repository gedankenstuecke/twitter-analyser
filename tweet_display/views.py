from django.http import HttpResponse
from django.shortcuts import render, redirect

from .models import Graph
from .helper import grant_access

# Create your views here.


def index(request, oh_id=None):
    context = {'section': 'general'}
    if oh_id is not None:
        context['link_target'] = oh_id
    if grant_access(request, oh_id):
        context['oh_id'] = grant_access(request, oh_id)
        return render(request, 'tweet_display/index.html', context)
    else:
        return redirect('/users/')


def location(request, oh_id=None):
    context = {'section': 'location'}
    if oh_id is not None:
        context['link_target'] = oh_id
    if grant_access(request, oh_id):
        context['oh_id'] = grant_access(request, oh_id)
        return render(request, 'tweet_display/location.html', context)
    else:
        return redirect('/users/')


def interactions(request, oh_id=None):
    context = {'section': 'interactions'}
    if oh_id is not None:
        context['link_target'] = oh_id
    if grant_access(request, oh_id):
        context['oh_id'] = grant_access(request, oh_id)
        return render(request, 'tweet_display/interactions.html', context)
    else:
        return redirect('/users/')


def gender_rt(request, oh_id):
    if grant_access(request, oh_id):
        graph = Graph.objects.filter(graph_type__exact='gender_rt')[0]
        return HttpResponse(graph.graph_data, content_type='application/json')
    else:
        return redirect('/users/')


def gender_reply(request, oh_id):
    if grant_access(request, oh_id):
        graph = Graph.objects.filter(graph_type__exact='gender_reply')[0]
        return HttpResponse(graph.graph_data, content_type='application/json')
    else:
        return redirect('/users')


def hourly_tweets(request, oh_id):
    if grant_access(request, oh_id):
        graph = Graph.objects.filter(graph_type__exact='hourly_tweets')[0]
        return HttpResponse(graph.graph_data, content_type='application/json')
    else:
        return redirect('/users/')


def tweet_types(request, oh_id):
    if grant_access(request, oh_id):
        graph = Graph.objects.filter(graph_type__exact='tweet_types')[0]
        return HttpResponse(graph.graph_data, content_type='application/json')
    else:
        return redirect('/users/')


def top_replies(request, oh_id):
    if grant_access(request, oh_id):
        graph = Graph.objects.filter(graph_type__exact='top_replies')[0]
        return HttpResponse(graph.graph_data, content_type='application/json')
    else:
        return redirect('/users/')


def heatmap(request, oh_id):
    if grant_access(request, oh_id):
        graph = Graph.objects.filter(graph_type__exact='heatmap')[0]
        return HttpResponse(graph.graph_data, content_type='application/json')
    else:
        return redirect('/users/')


def timeline(request, oh_id):
    if grant_access(request, oh_id):
        graph = Graph.objects.filter(graph_type__exact='timeline')[0]
        return HttpResponse(graph.graph_data, content_type='application/json')
    else:
        return redirect('/users/')


def overall_tweets(request, oh_id):
    if grant_access(request, oh_id):
        graph = Graph.objects.filter(graph_type__exact='overall_tweets')[0]
        return HttpResponse(graph.graph_data, content_type='application/json')
    else:
        return redirect('/users/')

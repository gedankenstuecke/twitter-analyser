# from django.http import HttpResponse
from django.shortcuts import render  # redirect


def about(request):
    context = {'section': 'about'}
    return render(request, 'twitteranalyser/about.html', context)

# from django.http import HttpResponse
from django.shortcuts import render  # redirect
from django.conf import settings


def about(request):
    context = {'section': 'about',
               'oh_proj_page': settings.OH_ACTIVITY_PAGE}
    return render(request, 'twitteranalyser/about.html', context)

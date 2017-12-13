from django.conf.urls import url
from django.views.generic.base import RedirectView
from . import views


urlpatterns = [
    url(r'^index/$', views.index, name='index'),
    url(r'^index/(?P<oh_id>\w+)/$',
        views.index,
        name='index_w_id'),
    url(r'^location/$', views.location, name='location'),
    url(r'^location/(?P<oh_id>\w+)/$', views.location, name='location_w_id'),
    url(r'^interactions/$', views.interactions, name='interactions'),
    url(r'^interactions/(?P<oh_id>\w+)/$',
        views.interactions,
        name='interactions_w_id'),
    url(r'^gender_rt/(?P<oh_id>\w+)/$', views.gender_rt, name='gender_rt'),
    url(r'^gender_reply/(?P<oh_id>\w+)/$',
        views.gender_reply,
        name='gender_reply'),
    url(r'^hourly_tweets/(?P<oh_id>\w+)/$',
        views.hourly_tweets,
        name='hourly_tweets'),
    url(r'^tweet_types/(?P<oh_id>\w+)/$',
        views.tweet_types,
        name='tweet_types'),
    url(r'^top_replies/(?P<oh_id>\w+)/$',
        views.top_replies,
        name='top_replies'),
    url(r'^heatmap/(?P<oh_id>\w+)/$', views.heatmap, name='heatmap'),
    url(r'^timeline/(?P<oh_id>\w+)/$', views.timeline, name='timeline'),
    url(r'^overall_tweets/(?P<oh_id>\w+)/$',
        views.overall_tweets,
        name='overall_tweets'),
    url(r'^$', RedirectView.as_view(pattern_name='index', permanent=False))
]

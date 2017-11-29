from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^gender_rt/$', views.gender_rt, name='gender_rt'),
    url(r'^gender_reply/$', views.gender_reply, name='gender_reply'),
    url(r'^hourly_tweets/$', views.hourly_tweets, name='hourly_tweets'),

]

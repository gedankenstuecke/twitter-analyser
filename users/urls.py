from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='user_home'),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'complete/?$', views.complete),
    url(r'delete/?$', views.delete_account, name='user.delete'),
    url(r'access_switch/?$', views.access_switch, name='user.access'),
]

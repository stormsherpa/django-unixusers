from django.conf.urls import patterns, url

from django_unixusers import views

urlpatterns = patterns('',
    url(r'^login/$', 'django.contrib.auth.views.login',
        {'template_name': 'django_unixusers/login.html'}, name='account_login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout',
        {'template_name': 'django_unixusers/logout.html'}, name='account_logout'),
    url(r'^signup/$', views.SignupView.as_view(), name='signup'),
    url(r'^profile/$', views.ProfileView.as_view(), name='profile'),
)
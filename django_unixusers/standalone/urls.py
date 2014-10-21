from django.conf.urls import patterns, include, url
from django.contrib import admin

import django_unixusers.urls
from django_unixusers.views import FrontPageView

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'django_unixusers.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', FrontPageView.as_view(), name='main'),
    url(r'^accounts/', include(django_unixusers.urls)),
    url(r'^admin/', include(admin.site.urls)),
)

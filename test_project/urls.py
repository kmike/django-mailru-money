# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url, include

urlpatterns = patterns('',
    url(r'^mailru-money/', include('mailru_money.urls')),
)

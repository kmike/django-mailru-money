# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.conf.urls.defaults import patterns, url
from .views import mailru_money_result

urlpatterns = patterns('',
    url(r'^result/$', mailru_money_result, name='mailru_money_result'),
    url(r'^result-order/$', mailru_money_result, name='mailru_money_result_order'),
)

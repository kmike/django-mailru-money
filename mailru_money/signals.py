# -*- coding: utf-8 -*-
from django.dispatch import Signal
result_success = Signal(providing_args=['request', 'form'])
result_failure = Signal(providing_args=['request', 'form'])

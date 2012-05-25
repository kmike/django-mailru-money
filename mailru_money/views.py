# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import ResultForm
from . import signals

logger = logging.getLogger(__name__)

def _ResultResponse(is_accepted, form, error_code=None):
    response_lines = []

    try:
        item_number = form.cleaned_data['item_number']
        response_lines.append('item_number=' + item_number)
    except (AttributeError, KeyError):
        pass

    if is_accepted:
        response_lines.append('status=ACCEPTED')
    else:
        response_lines.append('status=REJECTED')

    if error_code:
        response_lines.append('code='+error_code)

    return HttpResponse("\n".join(response_lines))


@csrf_exempt
def mailru_money_result(request, form_cls=ResultForm):
    """
    Result URL handler.

    On successful access `mailru_money.signals.result_success` signal is sent.
    Orders should be processed in signal handler.
    """
    form = form_cls(request.POST)
    signal_kwargs = dict(
        sender = mailru_money_result,
        form = form,
        request = request
    )

    try:
        if form.is_valid():
            form.save()
            signals.result_success.send(**signal_kwargs)
            return _ResultResponse(True, form)

        # form is invalid
        signals.result_failure.send(**signal_kwargs)

        return _ResultResponse(False, form, form.error_code())

    except Exception as e:
        logger.error(e)
        return _ResultResponse(False, form, 'S0001')



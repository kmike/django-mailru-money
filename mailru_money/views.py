# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import ResultForm, OrderResultForm, ERROR_GENERIC
from . import signals, settings

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
def mailru_money_result(request, form_cls=OrderResultForm):
    """
    Result URL handler. By default assumes that MailruOrderForm
    was used to create an order (pass form_cls=ResultForm if that
    is not the case).

    If order state is changed then ``order_status_changed`` signal
    will be sent. It can be used to handle the payment, e.g.::

        from mailru_money.signals import order_status_changed
        from mailru_money.models import MailruOrder

        def order_handler(sender, order, old_status, **kwargs):
            if order.state == MailruOrder.PAID:
                # order is payed, deliver an item
                order.pay_for.deliver()
            elif order.state == MailruOrder.REJECTED:
                order.pay_for.unblock()

        order_status_changed.connect(order_handler)

    Extra signals (result_success and result_failure) can be used for
    less trivial order processing.
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
        return _ResultResponse(False, form, ERROR_GENERIC)


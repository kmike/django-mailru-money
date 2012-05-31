# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
import base64
from decimal import Decimal
from django import forms
from mailru_money import settings, api
from mailru_money.models import Notification, MailruOrder

def _to_decimal(amount):
    # python 2.6 is not able to convert floats to decimals directly
    if isinstance(amount, float):
        return Decimal("%.15g" % amount)
    return Decimal(amount)


class HiddenForm(forms.Form):
    """ A form with all fields hidden """
    def __init__(self, *args, **kwargs):
        super(HiddenForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget = forms.HiddenInput()


class MailruMoneyForm(HiddenForm):
    """
    Low-level money.mail.ru helper form. It is not for validating data.
    It can be used to output html.

    Pass all the fields to the form's 'initial' argument::

        form = MailruMoneyForm(initial={
            'description': u'Заказ',
            'issuer_id': u'543-TSH',
            'message': u'Покупка',
            'sum': str(15.5),
        })

    """
    ACTION = 'https://money.mail.ru/pay/light/'
    SECRET_KEY = settings.MAILRU_MONEY_SECRET_KEY
    DEFAULT_SHOP_ID = settings.MAILRU_MONEY_SHOP_ID
    DEFAULT_CURRENCY = 'RUR'

    shop_id = forms.CharField()
    currency = forms.CharField()
    sum = forms.CharField()
    description = forms.CharField()
    issuer_id = forms.CharField()
    signature = forms.CharField()
    message = forms.CharField(required=False)
    keep_uniq = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        kwargs['initial'].setdefault('shop_id', self.DEFAULT_SHOP_ID)
        kwargs['initial'].setdefault('currency', self.DEFAULT_CURRENCY)

        super(MailruMoneyForm, self).__init__(*args, **kwargs)

        for key in 'keep_uniq', 'message':
            if key not in self.initial:
                del self.fields[key]

        signature = api.signature(self.SECRET_KEY, self.initial, hash_secret=True)
        self.fields['signature'].initial = signature


class MailruOrderForm(MailruMoneyForm):
    """
    High-level money.mail.ru helper form.
    Auto-creates MailruOrder instances.

    ::

        item = Item.objects.get(pk=item_pk)
        form = MailruOrderForm(15, u'оплата товара',
            user = request.user,
            pay_for = item,
        )

    """
    def __init__(self, amount, description, user=None, pay_for=None, message=None, currency='RUR'):
        self.order = MailruOrder.objects.create(
            amount = _to_decimal(amount),
            description = description,
            user = user,
            pay_for = pay_for,
            message = message,
            currency = currency,
        )
        initial={
            'amount': str(amount),
            'description': description,
            'issuer_id': str(self.order.issuer_id),
            'keep_uniq': '1',
            'currency': currency,
        }
        if message is not None:
            initial['message'] = message
        super(MailruOrderForm, self).__init__(initial=initial)


class ResultForm(forms.ModelForm):
    SECRET_KEY = settings.MAILRU_MONEY_SECRET_KEY

    signature = forms.CharField()
    url_pay = forms.URLField(required=False)

    class Meta:
        model = Notification
        fields = 'type', 'status', 'item_number', 'issuer_id', 'serial', 'auth_method'

#    def clean_item_number(self):
#        item_number = self.cleaned_data['item_number']
#        if SuccessNotification.objects.filter(item_number=item_number).exists():
#            raise forms.ValidationError('S0004')
#        return self.cleaned_data['item_number']

    def clean_issuer_id(self):
        issuer_id = self.cleaned_data['issuer_id']
        if issuer_id:
            try:
                issuer_id.encode('ascii')
            except Exception as e:
                raise forms.ValidationError(e)
        return self.cleaned_data['issuer_id']

    def clean(self):
        sig = api.signature(self.SECRET_KEY, self.cleaned_data, hash_secret=False)
        if sig != self.cleaned_data['signature']:
            raise forms.ValidationError('S0003')

        self.post_clean_issuer_id()
        return self.cleaned_data

    def post_clean_issuer_id(self):
        issuer_id = self.cleaned_data['issuer_id']
        self.cleaned_data['issuer_id'] = base64.b64decode(issuer_id.encode('ascii'))

    def error_code(self):
        if 'item_number' in self.errors and self.errors['item_number'][0] == 'S0004':
            return 'S0004'

        if 'signature' in self.errors and self.errors['signature'][0] == 'S0003':
            return 'S0003'

        return 'S0002'

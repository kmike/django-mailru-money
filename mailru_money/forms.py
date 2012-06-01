# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
import base64
from decimal import Decimal
from django import forms
from mailru_money import settings, api
from mailru_money.models import Notification, MailruOrder

ERROR_GENERIC = 'S0001' # Техническая ошибка на стороне Магазина (например, недоступна база данных)
ERROR_INVALID_NOTIFICATION = 'S0002' # Некорректный формат уведомления (например, не получен item_number)
ERROR_SIGNATURE = 'S0003' # Ошибка проверки цифровой подписи
ERROR_DUPLICATE_ITEM = 'S0004' # Уведомление с указанным item_number уже обработано. Остановить уведомления

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
            user = user,
            pay_for = pay_for,
            currency = currency,
        )
        initial={
            'sum': str(amount),
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

    @classmethod
    def _get_signature(cls, data):
        return api.signature(cls.SECRET_KEY, data, hash_secret=False)

    def clean(self):
        sig = self._get_signature(self.cleaned_data)
        if sig != self.cleaned_data['signature']:
            raise forms.ValidationError(ERROR_SIGNATURE)

        self.post_clean_issuer_id()
        return self.cleaned_data

    def post_clean_issuer_id(self):
        issuer_id = self.cleaned_data['issuer_id']
        self.cleaned_data['issuer_id'] = base64.b64decode(issuer_id.encode('ascii'))

    def error_code(self):
        if ERROR_DUPLICATE_ITEM in self.errors.get('item_number', []):
            return ERROR_DUPLICATE_ITEM

        if ERROR_DUPLICATE_ITEM in self.non_field_errors():
            return ERROR_DUPLICATE_ITEM

        if ERROR_SIGNATURE in self.errors.get('signature', []):
            return ERROR_SIGNATURE

        return ERROR_INVALID_NOTIFICATION


class OrderResultForm(ResultForm):
    """
    Result form with mandatory MoneyOrder handling.
    """
    def clean(self):
        data = super(OrderResultForm, self).clean()
        issuer_id = data['issuer_id']
        try:
            self._order = MailruOrder.objects.get(issuer_id=issuer_id)
        except (MailruOrder.DoesNotExist, ValueError):
            raise forms.ValidationError(ERROR_INVALID_NOTIFICATION)
        return data

    def save(self, commit=True):
        assert commit==True, 'commit=False is not supported'
        notification = super(OrderResultForm, self).save(commit)
        notification._update_order(self._order)
        return notification



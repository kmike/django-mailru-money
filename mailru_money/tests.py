# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.utils import unittest
from django.db import models
from django.test import TestCase
from mailru_money import api, forms
from mailru_money.models import MailruOrder, Notification

SECRET_KEY = 'secret_key'
SIGNATURE = '93e6332ab1e719b2e6244ffe0ab12045349f425f'
PARAMS = {
    'currency': 'RUR',
    'description': 'Заказ',
    'issuer_id': '543-TSH',
    'message': 'Покупка',
    'shop_id': '12345',
    'sum': '10.00',
}

class TestMailruMoneyForm(forms.MailruMoneyForm):
    SECRET_KEY = SECRET_KEY


class ApiTest(unittest.TestCase):
    def test_signature(self):
        sig = api.signature(SECRET_KEY, PARAMS)
        self.assertEqual(sig, SIGNATURE)


class FormTest(unittest.TestCase):
    def test_form(self):

        initial = PARAMS.copy()
        del initial['currency'] # it should be reset to the default value

        form = TestMailruMoneyForm(initial=initial)
        form_rendered = form.as_p()

        self.assertIn(SIGNATURE, form_rendered)
        self.assertNotIn('keep_uniq', form_rendered)


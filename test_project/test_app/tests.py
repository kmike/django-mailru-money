# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import RequestFactory
from mailru_money.models import Notification
from mailru_money.forms import ResultForm
from mailru_money.views import mailru_money_result
from mailru_money import signals

# Test data from official example.
# It is incorrect because issuer_id is not properly base64-encoded.
ORIGINAL_TEST_DATA = {
    'type': Notification.INVOICE,
    'status': Notification.PAID,
    'item_number': '123456',
    'issuer_id': 'aBcDeF012',
    'serial': '111',
    'auth_method': Notification.SHA,
    'signature': 'ffc4ca62571508a35e6548696039749da3349362',
}

TEST_DATA = ORIGINAL_TEST_DATA.copy()
TEST_DATA['issuer_id'] = 'NTQzLVRTSA==' # base64encode('543-TSH')
TEST_DATA['signature'] = '62994d92ca50f9bd626acf82f2b6a25affbd5ae9'

class TestResultForm(ResultForm):
    SECRET_KEY = 'secret_key'

class NoBase64DecodeResultForm(TestResultForm):
    def post_clean_issuer_id(self):
        pass


class MailruMoneyTest(TestCase):

    def test_recieve_result_success_original(self):
        self.assertEqual(Notification.objects.count(), 0)

        url = reverse('mailru_money_result')
        rf = RequestFactory()
        request = rf.post(url, ORIGINAL_TEST_DATA)

        resp = mailru_money_result(request, form_cls=NoBase64DecodeResultForm)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('ACCEPTED', str(resp))

        self.assertEqual(Notification.objects.count(), 1)

    def test_recieve_result_success(self):

        def success_handler(sender, request, form, **kwargs):
            self.assertEqual(form.instance.item_number, '123456')
        signals.result_success.connect(success_handler)

        url = reverse('mailru_money_result')
        rf = RequestFactory()
        request = rf.post(url, TEST_DATA)

        resp = mailru_money_result(request, form_cls=TestResultForm)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('ACCEPTED', str(resp))

        self.assertEqual(Notification.objects.count(), 1)

        notification = Notification.objects.all()[0]
        self.assertEqual(notification.issuer_id, '543-TSH')


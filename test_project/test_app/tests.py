# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import base64
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import RequestFactory

from mailru_money.models import Notification, MailruOrder
from mailru_money.forms import ResultForm, MailruOrderForm, OrderResultForm
from mailru_money.views import mailru_money_result
from mailru_money import signals

from test_project.test_app.models import Item

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

class TestResultOrderForm(OrderResultForm):
    SECRET_KEY = 'secret_key'

class NoBase64DecodeResultForm(TestResultForm):
    def post_clean_issuer_id(self):
        pass


class MailruMoneyTest(TestCase):

    def _notify_request(self, data):
        url = reverse('mailru_money_result')
        rf = RequestFactory()
        return rf.post(url, data)

    def assertAccepted(self, resp):
        self.assertEqual(resp.status_code, 200)
        self.assertIn('ACCEPTED', str(resp))

    def assertNotificationError(self, resp, erorr_code):
        self.assertEqual(resp.status_code, 200)
        self.assertIn('REJECTED', str(resp))
        self.assertIn(erorr_code, str(resp))


    def test_recieve_result_success_original(self):
        self.assertEqual(Notification.objects.count(), 0)

        request = self._notify_request(ORIGINAL_TEST_DATA)

        resp = mailru_money_result(request, form_cls=NoBase64DecodeResultForm)
        self.assertAccepted(resp)

        self.assertEqual(Notification.objects.count(), 1)

    def test_recieve_result_success(self):

        def success_handler(sender, request, form, **kwargs):
            self.assertEqual(form.instance.item_number, '123456')
        signals.result_success.connect(success_handler)

        request = self._notify_request(TEST_DATA)

        resp = mailru_money_result(request, form_cls=TestResultForm)
        self.assertAccepted(resp)

        self.assertEqual(Notification.objects.count(), 1)

        notification = Notification.objects.all()[0]
        self.assertEqual(notification.issuer_id, '543-TSH')

    def test_mailru_orders(self):
        item = Item.objects.create(name='хомяк')

        calls = {'cnt': 0}
        def payment_handler(sender, order, old_status, **kwargs):
            self.assertEqual(order.status, MailruOrder.PAID)
            self.assertEqual(old_status, MailruOrder.UNKNOWN)
            self.assertEqual(order.pay_for, item)
            calls['cnt'] += 1

        signals.order_status_changed.connect(payment_handler)

        form = MailruOrderForm(100, 'description', pay_for=item, message='купи слона')
        # ... form is shown to user

        # invalid notification: issuer_id is not correct
        request = self._notify_request(TEST_DATA)
        resp = mailru_money_result(request, form_cls=TestResultOrderForm)
        self.assertNotificationError(resp, 'S0002')

        # another invalid notification: issuer_id is not in database
        INVALID_DATA = TEST_DATA.copy()
        INVALID_DATA['issuer_id'] = base64.b64encode(b'11111').decode('ascii')
        INVALID_DATA['signature'] = TestResultOrderForm._get_signature(INVALID_DATA)

        request = self._notify_request(INVALID_DATA)
        resp = mailru_money_result(request, form_cls=TestResultOrderForm)
        self.assertNotificationError(resp, 'S0002')

        # valid request
        DATA = TEST_DATA.copy()
        DATA['issuer_id'] = base64.b64encode(str(form.order.issuer_id).encode('ascii')).decode('ascii')
        DATA['signature'] = TestResultOrderForm._get_signature(DATA)

        request = self._notify_request(DATA)
        resp = mailru_money_result(request, form_cls=TestResultOrderForm)
        self.assertAccepted(resp)
        self.assertEqual(calls['cnt'], 1)


class OrderTest(TestCase):
    def test_order_form(self):
        item = Item.objects.create(name='хомячок')
        form = MailruOrderForm(100, 'аренда хомячка', pay_for=item)
        self.assertEqual(form.order.amount, 100)

        notification = Notification.objects.create(
            type = Notification.PAYMENT,
            status = Notification.PAID,
            item_number = '123',
            issuer_id = form.order.pk,
            serial = '123',
            auth_method = Notification.SHA
        )

        # reload order
        order = MailruOrder.objects.get(pk=form.order.pk)
        self.assertEqual(notification.mailru_order(), order)
        self.assertEqual(order.pay_for, item)



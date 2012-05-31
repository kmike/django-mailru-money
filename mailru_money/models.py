# -*- coding: utf-8 -*-
import logging
from django.contrib.auth.models import User
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from .signals import order_status_changed
from . import settings

logger = logging.getLogger(__name__)

class Notification(models.Model):
    INVOICE = 'INVOICE'
    PAYMENT = 'PAYMENT'
    TYPE_CHOICES = (
        (INVOICE, 'INVOICE'),
        (PAYMENT, 'PAYMENT'),
    )

    DELIVERED = 'DELIVERED'
    PAID = 'PAID'
    REJECTED = 'REJECTED'
    STATUS_CHOICES = (
        (DELIVERED, 'DELIVERED'),
        (PAID, 'PAID'),
        (REJECTED, 'REJECTED'),
    )

    SHA = 'SHA'
    AUTH_METHOD_CHOICES = (
        (SHA, 'SHA'),
    )

    type = models.CharField(max_length=15, choices=TYPE_CHOICES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES)
    item_number = models.CharField(max_length=30, db_index=True)
    issuer_id = models.CharField(max_length=30, db_index=True)
    serial = models.CharField(max_length=15)
    auth_method = models.CharField(max_length=10, choices=AUTH_METHOD_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'money.mail.ru notification'
        verbose_name_plural = 'money.mail.ru notifications'

    def __unicode__(self):
        return 'money.mail.ru notification #%s' % self.pk

    def mailru_order(self):
        try:
            issuer_id = int(self.issuer_id)
        except ValueError:
            raise MailruOrder.DoesNotExist()
        return MailruOrder.objects.get(issuer_id=issuer_id)

    def _update_order(self, order):
        STATUS_MAPPING = {
            Notification.PAID: MailruOrder.PAID,
            Notification.REJECTED: MailruOrder.REJECTED,
            Notification.DELIVERED: MailruOrder.DELIVERED,
        }
        order.set_status(STATUS_MAPPING[self.status])


class MailruOrder(models.Model):
    PAID = 'PAID'
    REJECTED = 'REJECTED'
    DELIVERED = 'DELIVERED'
    UNKNOWN = 'UNKNOWN'

    STATUS_CHOICES = (
        (UNKNOWN, 'UNKNOWN'),
        (DELIVERED, 'DELIVERED'),
        (PAID, 'PAID'),
        (REJECTED, 'REJECTED'),
    )

    ALLOWED_STATUS_CHANGES = {
        PAID: set(),
        REJECTED: set([PAID, DELIVERED]),
        DELIVERED: set([PAID, REJECTED]),
        UNKNOWN: set([PAID, REJECTED, DELIVERED]),
    }

    issuer_id = models.AutoField(primary_key=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=15, default='RUR')

    status = models.CharField(max_length=10, db_index=True, default=UNKNOWN, choices=STATUS_CHOICES)

    user = models.ForeignKey(User, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    pay_for = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = 'money.mail.ru order'
        verbose_name_plural = 'money.mail.ru orders'

    def __unicode__(self):
        return 'money.mail.ru order #%s' % self.pk

    def set_status(self, new_status):
        """
        Sets status to new_status if the transition is allowed;
        does nothing otherwise.
        """
        alowed_changes = self.ALLOWED_STATUS_CHANGES[self.status]
        if new_status in alowed_changes:
            old_status = self.status
            self.status = new_status
            self.save()
            order_status_changed.send(
                sender=self.__class__,
                order=self,
                old_status=old_status
            )


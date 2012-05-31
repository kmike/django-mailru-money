# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

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

    def mailru_order(self):
        return MailruOrder.objects.get(issuer_id=self.issuer_id)



class MailruOrder(models.Model):
    issuer_id = models.AutoField(primary_key=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=15, default='RUR')
    description = models.TextField()
    message = models.TextField(null=True, blank=True, default='')

    user = models.ForeignKey(User, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    pay_for = GenericForeignKey('content_type', 'object_id')


    class Meta:
        verbose_name = 'money.mail.ru order'
        verbose_name_plural = 'money.mail.ru orders'

    def is_paid(self):
        return Notification.objects.filter(
            issuer_id=self.issuer_id,
            status=Notification.PAID
        ).exists()
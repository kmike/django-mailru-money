# -*- coding: utf-8 -*-
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


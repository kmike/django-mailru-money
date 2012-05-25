# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.contrib import admin
from mailru_money.models import Notification

class NotificationAdmin(admin.ModelAdmin):
    list_display = ['serial', 'item_number', 'issuer_id', 'type', 'status', 'created_at']
    list_filter = ['type', 'status', 'auth_method']
    search_fields = ['item_number', 'issuer_id']

admin.site.register(Notification, NotificationAdmin)
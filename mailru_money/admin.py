# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.contrib import admin

try:
    from salmonella.admin import SalmonellaMixin
except ImportError:
    class SalmonellaMixin(object):
        pass

from mailru_money.models import Notification, MailruOrder

class NotificationAdmin(admin.ModelAdmin):
    list_display = ['serial', 'item_number', 'issuer_id', 'type', 'status', 'created_at']
    list_filter = ['type', 'status', 'auth_method']
    search_fields = ['item_number', 'issuer_id']
    ordering = ['-item_number']

class MailruOrderAdmin(SalmonellaMixin, admin.ModelAdmin):
    list_display = ['issuer_id', 'amount', 'user', 'created_at']
    readonly_fields = ['user']
    salmonella_fields = ['user']
    ordering = ['-issuer_id']

admin.site.register(MailruOrder, MailruOrderAdmin)
admin.site.register(Notification, NotificationAdmin)
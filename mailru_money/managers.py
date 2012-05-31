# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.db import models

class MoneyOrderManager(models.Manager):
    def paid(self):
        pass
#        return self.get_query_set().filter()
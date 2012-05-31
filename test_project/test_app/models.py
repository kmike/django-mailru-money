# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=30)


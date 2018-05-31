# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models


class Project(models.Model):
    user = models.OneToOneField(User, models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    share = models.BooleanField(default=False)
    thumbnail = models.CharField(max_length=100)
    owner = models.CharField(max_length=50)
    screen = models.CharField(max_length=10, blank=True)
    density = models.CharField(max_length=10, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    uuid = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return str(self.email) + ', ' + str(self.project)


# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models


class Project(models.Model):
    user = models.ForeignKey(User, related_name='user')
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    thumbnail = models.CharField(max_length=200, default='exegesis/static/project.jpg')
    owner = models.CharField(max_length=50)
    screen = models.CharField(max_length=10, null=True, blank=True)
    density = models.CharField(max_length=10, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    uuid = models.CharField(max_length=50, blank=True)
    shared_users = models.ManyToManyField(User, related_name='shared_users', blank=True)

    def __str__(self):
        return str(self.name) + ' --> ' + str(self.user)


class ArtBoard(models.Model):
    project = models.ForeignKey(Project)
    name = models.CharField(max_length=50)
    location = models.CharField(max_length=200)
    uuid = models.CharField(max_length=50, blank=True)
    latest = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name) + ' --> ' + str(self.location) + ' --> ' + str(self.project)


class Revision(models.Model):
    name = models.CharField(max_length=50)
    artboard = models.ForeignKey(ArtBoard)

    def __str__(self):
        return str(self.name) + ', ' + str(self.artboard)


class Note(models.Model):
    user = models.ForeignKey(User)
    note = models.CharField(max_length=200)
    artboard = models.ForeignKey(ArtBoard)

    def __str__(self):
        return str(self.note) + ', ' + str(self.email)


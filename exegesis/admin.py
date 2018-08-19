# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from exegesis.models import Project, ArtBoard, Revision, Note

admin.site.register(Project)
admin.site.register(ArtBoard)
admin.site.register(Revision)
admin.site.register(Note)
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Sitio

# Register your models here.

@admin.register(Sitio)
class SitioAdmin(admin.ModelAdmin):
    pass


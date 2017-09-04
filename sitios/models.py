# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Sitio(models.Model):
    url = models.URLField(help_text='Sitio a monitorear. Ej. https://www.google.com/', verbose_name='URL')
    frecuencia = models.IntegerField(help_text='Frecuencia de monitoreo en segundos', default=10, blank=False, null=False)
    timeout = models.IntegerField(help_text='Timeout en segundos.', default=10, blank=False, null=False)

    def __unicode__(self):
        return self.url

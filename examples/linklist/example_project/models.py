from __future__ import unicode_literals
from django.db import models
from django.template.defaultfilters import slugify

from anylink.fields import AnyLinkField

import six


@six.python_2_unicode_compatible
class LinkableObject(models.Model):
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.description

    def get_absolute_url(self):
        return u'/{0}/{1}/'.format(self.pk, slugify(self.description))


@six.python_2_unicode_compatible
class Linklist(models.Model):
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.description


@six.python_2_unicode_compatible
class Link(models.Model):
    linklist = models.ForeignKey(Linklist, on_delete=models.CASCADE)

    link = AnyLinkField()

    def __str__(self):
        return str(self.link)

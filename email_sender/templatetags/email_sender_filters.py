import os

from django.template import library


register = library.Library()


@register.filter
def filename(value):
    return os.path.basename(value.name)

from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

import django_filters

from .models import Recipient


class CustomBooleanWidget(django_filters.widgets.BooleanWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.choices = (('', _('---------')), ('True', _('Yes')), ('False', _('No')))


class RecipientFilter(django_filters.FilterSet):
    class Meta:
        model = Recipient
        fields = ('user__groups',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = self.queryset.filter(email__isnull=False).exclude(email='')

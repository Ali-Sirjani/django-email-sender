from django.db import models
from django.utils.translation import gettext_lazy as _

from tinymce.models import HTMLField

from ..abstracts import TimestampedModel


class MsgRecord(TimestampedModel):
    subject = models.CharField(max_length=255, verbose_name=_('subject'))
    message = HTMLField(verbose_name=_('message'))
    recipients = models.JSONField(verbose_name=_('recipients'))
    is_sent = models.BooleanField(default=False, verbose_name=_('is sent'))

    def __str__(self):
        return self.subject

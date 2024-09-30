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


class MsgRecordImage(TimestampedModel):
    msg_record = models.ForeignKey(MsgRecord, on_delete=models.CASCADE, related_name='images',
                                   verbose_name=_('record images'))

    img = models.ImageField(upload_to='msg_record_images/', verbose_name=_('image'))

    class Meta:
        verbose_name = _('message record image')
        verbose_name_plural = _('message record images')
        ordering = ('datetime_created',)


class MsgRecordFile(TimestampedModel):
    msg_record = models.ForeignKey(MsgRecord, on_delete=models.CASCADE, related_name='files',
                                   verbose_name=_('record images'))

    file = models.FileField(upload_to='msg_record_files/', verbose_name=_('file'))

    class Meta:
        verbose_name = _('message record file')
        verbose_name_plural = _('message record files')
        ordering = ('datetime_created',)

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Recipient, MsgRecord, MsgRecordImage, MsgRecordFile


class MsgRecordImageInline(admin.TabularInline):
    model = MsgRecordImage
    extra = 1
    readonly_fields = ('datetime_created', 'datetime_updated')


class MsgRecordFileInline(admin.TabularInline):
    model = MsgRecordFile
    extra = 1
    readonly_fields = ('datetime_created', 'datetime_updated')


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    pass


@admin.register(MsgRecord)
class MsgRecordAdmin(admin.ModelAdmin):
    inlines = (MsgRecordImageInline, MsgRecordFileInline)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['datetime_created', 'datetime_updated']
        if obj and obj.is_sent:
            readonly_fields.extend(['subject', 'get_message', 'recipients', 'is_sent'])

        return readonly_fields

    def get_fields(self, request, obj=None):
        fields = ['subject', 'message', 'recipients', 'is_sent', 'datetime_created', 'datetime_updated']
        if obj and obj.is_sent:
            # when obj is sent, replace message with get_message
            # for show rich text correctly
            fields[1] = 'get_message'

        return fields

    def get_message(self, obj):
        """use for when obj is sent and message must display as readonly field"""
        return format_html(obj.message)

    get_message.short_description = _('Message')

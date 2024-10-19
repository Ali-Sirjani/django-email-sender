import logging
import smtplib

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.forms import modelformset_factory
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model

from tinymce.models import HTMLField

from ..abstracts import TimestampedModel

logger = logging.getLogger(__name__)


class Recipient(TimestampedModel):
    user = models.OneToOneField(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                verbose_name=_('user'))

    email = models.EmailField(unique=True, verbose_name=_('email'))

    class Meta:
        verbose_name = _('Recipient')
        verbose_name_plural = _('Recipients')
        ordering = ('-datetime_created',)

    def __str__(self):
        if self.user:
            return f'{self.user}={self.email}'
        return f'{self.email}'


class MsgRecord(TimestampedModel):
    subject = models.CharField(max_length=255, verbose_name=_('subject'))
    message = HTMLField(verbose_name=_('message'))
    recipients = models.ManyToManyField(Recipient, related_name='recipients', verbose_name=_('recipients'))
    is_sent = models.BooleanField(default=False, verbose_name=_('is sent'))

    class Meta:
        verbose_name = _('message record')
        verbose_name_plural = _('message records')
        ordering = ('-datetime_created',)

    def __str__(self):
        return self.subject

    def save_attachments(self, formset, attr_name):
        for form in formset.forms:
            if form.cleaned_data.get(attr_name):
                msg_img_obj = form.save(commit=False)
                msg_img_obj.msg_record = self
                msg_img_obj.save()

    def send_email(self):
        # Prepare the email
        email = EmailMessage(
            subject=self.subject,
            body=self.message,
            to=self.recipients.values_list('email', flat=True),
        )

        email.content_subtype = 'html'

        # Attach images
        for msg_img in self.images.all():
            if msg_img.img:
                img_path = msg_img.img.path
                email.attach_file(img_path)

        # Attach files
        for msg_file in self.files.all():
            if msg_file.file:
                file_path = msg_file.file.path
                email.attach_file(file_path)

        try:
            email.send(fail_silently=False)
        except Exception as e:
            if isinstance(e, smtplib.SMTPAuthenticationError):
                logger.error(f"Failed to send email: {e}")
            else:
                logger.info(f"Failed to send email: {e}")
            self.is_sent = False
            raise
        else:
            self.is_sent = True

        self.save()


class MsgRecordImage(TimestampedModel):
    msg_record = models.ForeignKey(MsgRecord, on_delete=models.CASCADE, related_name='images',
                                   verbose_name=_('record images'))

    img = models.ImageField(upload_to='msg_record_images/', verbose_name=_('image'))

    class Meta:
        verbose_name = _('message record image')
        verbose_name_plural = _('message record images')
        ordering = ('datetime_created',)

    @classmethod
    def get_img_formset(cls, extra=2, max_num=3, data=None, files=None, queryset=None):
        """
        Creates and returns a modelformset for the MsgRecordImage model.

        Parameters:
            cls: The class object, referring to the MsgRecordImage model.
            extra (int): The number of empty, extra forms to display in the formset. Default is 3.
            max_num (int): The maximum number of forms allowed in the formset. Default is 3.
            data (QueryDict, optional): The POST data to bind to the formset, typically request.POST. Default is None.
            files (MultiValueDict, optional): The uploaded files to bind to the formset, typically request.FILES. Default is None.
            queryset (QuerySet, optional): A queryset of MsgRecordImage instances to pre-populate the formset. Default is None,
                                           meaning no records are fetched, and the formset is intended for creating new instances.

        Returns:
            ModelFormSet: A formset instance populated with the given data and files, or an empty formset if no data is provided.
        """
        from ..forms import MsgRecordImageForm

        # Create a formset factory for the MsgRecordImage model using the specified form.
        image_formset = modelformset_factory(cls, form=MsgRecordImageForm, extra=extra, max_num=max_num)
        if not queryset:
            queryset = cls.objects.none()

        # If data or files are provided (typically in a POST request), return a formset bound to this data.
        # Otherwise, return an unbound formset for a GET request or when no data/files are provided.
        if data or files:
            return image_formset(data, files, queryset=queryset)
        else:
            return image_formset(queryset=queryset)


class MsgRecordFile(TimestampedModel):
    msg_record = models.ForeignKey(MsgRecord, on_delete=models.CASCADE, related_name='files',
                                   verbose_name=_('record images'))

    file = models.FileField(upload_to='msg_record_files/', verbose_name=_('file'))

    class Meta:
        verbose_name = _('message record file')
        verbose_name_plural = _('message record files')
        ordering = ('datetime_created',)

    @classmethod
    def get_file_formset(cls, extra=2, max_num=3, data=None, files=None, queryset=None):
        """
        Creates and returns a modelformset for the MsgRecordFile model.

        Parameters:
            cls: The class object, referring to the MsgRecordFile model.
            extra (int): The number of empty, extra forms to display in the formset. Default is 3.
            max_num (int): The maximum number of forms allowed in the formset. Default is 3.
            data (QueryDict, optional): The POST data to bind to the formset, typically request.POST. Default is None.
            files (MultiValueDict, optional): The uploaded files to bind to the formset, typically request.FILES. Default is None.
            queryset (QuerySet, optional): A queryset of MsgRecordFile instances to pre-populate the formset. Default is None,
                                           meaning no records are fetched, and the formset is intended for creating new instances.

        Returns:
            ModelFormSet: A formset instance populated with the given data and files, or an empty formset if no data is provided.
        """
        from ..forms import MsgRecordFileForm

        # Create a formset factory for the MsgRecordFile model using the specified form.
        file_formset = modelformset_factory(cls, form=MsgRecordFileForm, extra=extra, max_num=max_num)
        if not queryset:
            queryset = cls.objects.none()

        # If data or files are provided (typically in a POST request), return a formset bound to this data.
        # Otherwise, return an unbound formset for a GET request or when no data/files are provided.
        if data or files:
            return file_formset(data, files, queryset=queryset)
        else:
            return file_formset(queryset=queryset)

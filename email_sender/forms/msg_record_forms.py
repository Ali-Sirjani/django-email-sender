from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth import get_user_model

from ..models import Recipient, MsgRecord, MsgRecordImage, MsgRecordFile


class MsgRecordForm(forms.ModelForm):
    recipients = forms.CharField(widget=forms.Textarea, required=True, help_text="Enter emails separated by commas")

    class Meta:
        model = MsgRecord
        exclude = ('is_sent',)

    def clean_recipients(self):
        # Get the raw input from the 'recipients' field and clean it by removing spaces, newlines, and carriage returns
        recipients_data = self.cleaned_data['recipients'].replace(' ', '').replace('\r', '').replace('\n', '')

        # Split the input data by commas and store it as a set to avoid duplicate entries
        entries = set(recipients_data.split(','))
        recipients_list = []
        entries.discard('')

        if entries:
            user_model = get_user_model()
            for entry in entries:
                try:
                    try:
                        # Attempt to split the entry into a username and email (if using the 'username:email' format)
                        username, email = entry.split(':')
                        try:
                            user = user_model.objects.get(username=username)
                            validate_email(email)
                            recipient, created = Recipient.objects.get_or_create(user=user, email=email)
                            recipients_list.append(recipient)
                        except user_model.DoesNotExist:
                            self.add_error('recipients', f'username "{username}" is invalid.')
                    except ValueError:
                        # If there's no username, assume the entry is an email-only format
                        email = entry
                        validate_email(email)
                        recipient, created = Recipient.objects.get_or_create(email=email)
                        recipients_list.append(recipient)
                except ValidationError as e:
                    self.add_error('recipients', e)
        else:
            self.add_error('recipients', _('the format is not correct'))

        return recipients_list


class MsgRecordImageForm(forms.ModelForm):
    img = forms.ImageField(label=_('image'), required=False)

    class Meta:
        model = MsgRecordImage
        fields = ('img',)

    def clean_img(self):
        img = self.cleaned_data.get('img')
        if img is False:
            return None  # Allow the field to be cleared
        return img


class MsgRecordFileForm(forms.ModelForm):
    file = forms.FileField(label=_('file'), required=False)

    class Meta:
        model = MsgRecordFile
        fields = ('file',)

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file is False:
            return None  # Allow the field to be cleared
        return file

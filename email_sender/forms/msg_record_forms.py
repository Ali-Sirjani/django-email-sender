from django import forms
from django.db import IntegrityError
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
        # Clean the raw input from 'recipients', removing spaces, newlines, and carriage returns
        recipients_data = self.cleaned_data['recipients'].replace(' ', '').replace('\r', '').replace('\n', '')

        # Split input by commas and store as a set to remove duplicates
        entries = set(recipients_data.split(','))
        recipients_list = []
        entries.discard('')  # Remove empty entries

        # Ensure there are valid entries, otherwise return an error
        if entries:
            user_model = get_user_model()

            for entry in entries:
                try:
                    try:
                        # Check if entry is in 'username:email' format by attempting to split on ':'
                        username, email = entry.split(':')
                        try:
                            # Get the user by the provided username
                            user = user_model.objects.get(username=username)

                            # Validate the email format
                            validate_email(email)

                            try:
                                # Try to get the recipient by email
                                recipient = Recipient.objects.get(email=email)

                                # If recipient exists but has no user, assign the user to the recipient
                                if not recipient.user:
                                    recipient.user = user
                                    recipient.save()

                                # If recipient exists with a different user, raise an error
                                elif recipient.user != user:
                                    self.add_error(
                                        'recipients',
                                        _(f'The user for email "{email}" is "{recipient.user}", but you entered "{user}".')
                                    )

                            except Recipient.DoesNotExist:
                                # If recipient doesn't exist, create a new recipient with the user and email
                                try:
                                    recipient = Recipient.objects.create(user=user, email=email)

                                except IntegrityError:
                                    # If there's an IntegrityError (user already exists), get the recipient by user
                                    recipient = Recipient.objects.get(user=user)

                                    # Update the recipient's email if necessary
                                    if user.email == email:
                                        recipient.email = email
                                        recipient.save()

                                    # If email doesn't match, raise an error
                                    else:
                                        self.add_error(
                                            'recipients',
                                            _(f'The email for user "{user}" is "{recipient.email}", but you entered "{email}".')
                                        )

                            # Add the recipient to the list
                            recipients_list.append(recipient)

                        # Handle case where the username does not exist
                        except user_model.DoesNotExist:
                            self.add_error('recipients', _(f'username "{username}" is invalid.'))

                    except ValueError:
                        # If there's no username, assume it's an email-only entry
                        email = entry
                        validate_email(email)  # Validate the email format

                        # Get or create recipient by email
                        recipient, created = Recipient.objects.get_or_create(email=email)
                        # Add the recipient to the list
                        recipients_list.append(recipient)

                # Handle any validation errors
                except ValidationError as e:
                    self.add_error('recipients', e)

        else:
            # Raise error if no valid entries
            self.add_error('recipients', _('The format is not correct'))

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

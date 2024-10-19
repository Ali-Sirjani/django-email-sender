from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db import transaction
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .models import MsgRecord, MsgRecordImage, MsgRecordFile
from .forms import MsgRecordForm
from .mixins import JSONResponseMixin


class MessagePanelView(LoginRequiredMixin, generic.ListView):
    model = MsgRecord
    paginate_by = 10
    template_name = 'email_sender/panel_msg.html'
    context_object_name = 'messages'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        context['msg_record_img_formset'] = MsgRecordImage.get_img_formset()
        context['msg_record_file_formset'] = MsgRecordFile.get_file_formset()
        context['msg_record_form'] = MsgRecordForm()

        return context


@login_required
@require_POST
def send_and_save_mgs_view(request):
    json_mixin_obj = JSONResponseMixin()

    request_post, request_files = request.POST, request.FILES
    msg_form = MsgRecordForm(request_post)
    msg_img_formset = MsgRecordImage.get_img_formset(data=request_post, files=request_files)
    msg_file_formset = MsgRecordFile.get_file_formset(data=request_post, files=request_files)

    if msg_form.is_valid() and msg_img_formset.is_valid() and msg_file_formset.is_valid():
        with transaction.atomic():
            # Save the message record
            msg_obj = msg_form.save()

            # Save the attachments (images and files)
            msg_obj.save_attachments(msg_img_formset, 'img')
            msg_obj.save_attachments(msg_file_formset, 'file')

            # Send the email after saving the message and attachments
            msg_obj.send_email()

            messages.success(request, _('Message successfully sent.'))
            return json_mixin_obj.render_to_json_response({'message': 'success'})

    # Handle form and formset errors
    response_data = {
        'msg_form': json_mixin_obj.ajax_response_form(msg_form),
        'msg_img_formset': [json_mixin_obj.ajax_response_form(msg_img_form) for msg_img_form in msg_img_formset.forms],
        'msg_file_formset': [json_mixin_obj.ajax_response_form(msg_file_form) for msg_file_form in msg_file_formset.forms],
    }

    return json_mixin_obj.render_to_json_response(response_data, status=400)

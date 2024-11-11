import json

from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.db.models import F

from .models import MsgRecord, MsgRecordImage, MsgRecordFile, Recipient
from .forms import MsgRecordForm
from .mixins import JSONResponseMixin
from .utils import DateTimeEncoder
from .filters import RecipientFilter


class MessagePanelView(LoginRequiredMixin, generic.ListView):
    model = MsgRecord
    paginate_by = 10
    template_name = 'email_sender/msg_panel_template.html'
    context_object_name = 'msg_list'
    queryset = MsgRecord.objects.filter(is_sent=True)

    def get_queryset(self):
        queryset = super().get_queryset()

        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(subject__icontains=q).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if not self.is_ajax():
            context['msg_record_img_formset'] = MsgRecordImage.get_img_formset()
            context['msg_record_file_formset'] = MsgRecordFile.get_file_formset()
            context['msg_record_form'] = MsgRecordForm()
            context['filter_recipient_form'] = RecipientFilter().form

        return context

    def is_ajax(self):
        return self.request.headers.get('x-requested-with') == 'XMLHttpRequest'

    def get(self, request, *args, **kwargs):
        if self.is_ajax():
            self.object_list = self.get_queryset()
            context = self.get_context_data(**kwargs)
            page_obj = context['page_obj']
            msg_query = context['msg_list'].values('id', 'subject', 'datetime_created')

            msg_list = [{**msg_obj, 'url': MsgRecord.objects.get(id=msg_obj['id']).get_absolute_url()} for msg_obj in
                        msg_query]

            return JsonResponse({
                'msg_list': json.dumps(msg_list, cls=DateTimeEncoder, date_format='%Y/%m/%d at %H:%M'),
                'page': page_obj.number,
                'total_pages': page_obj.paginator.num_pages,
                'has_previous': page_obj.has_previous(),
                'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
                'has_next': page_obj.has_next(),
                'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None
            })

        return super().get(request, *args, **kwargs)


@login_required
@require_POST
def send_and_save_mgs_view(request):
    json_mixin_obj = JSONResponseMixin()

    request_post, request_files = request.POST, request.FILES

    msg_form = MsgRecordForm(request_post)
    msg_img_formset = MsgRecordImage.get_img_formset(data=request_post, files=request_files)
    msg_file_formset = MsgRecordFile.get_file_formset(data=request_post, files=request_files)

    is_msg_send = MsgRecord.process_message(request_files.values(), msg_form, msg_img_formset, msg_file_formset)

    if is_msg_send:
        messages.success(request, _('Message successfully sent.'))
        return json_mixin_obj.render_to_json_response({'message': 'success'})

    # Handle form and formset errors
    response_data = {
        'msg_form': json_mixin_obj.ajax_response_form(msg_form),
        'msg_img_formset': [json_mixin_obj.ajax_response_form(f) for f in msg_img_formset.forms],
        'msg_file_formset': [json_mixin_obj.ajax_response_form(f) for f in msg_file_formset.forms],
    }

    return json_mixin_obj.render_to_json_response(response_data, status=400)


class MessageDetailView(generic.DetailView):
    model = MsgRecord
    template_name = 'email_sender/msg_detail.html'
    context_object_name = 'msg_obj'
    queryset = model.objects.prefetch_related('images', 'files')


@login_required
@require_GET
def filter_recipients_view(request):
    json_mixin_obj = JSONResponseMixin()
    filter_recipients = RecipientFilter(request.GET, Recipient.objects.all())
    recipients_data = filter_recipients.qs.values('email', username=F('user__username'))
    return json_mixin_obj.render_to_json_response({'recipients': json.dumps(list(recipients_data))})

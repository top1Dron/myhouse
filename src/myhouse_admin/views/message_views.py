import logging

from django.contrib.admin.views.decorators import staff_member_required
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.urls.base import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from myhouse_admin.forms.forms import MessageForm
from myhouse_admin.models import Floor, Message, Section
from myhouse_admin.utils import db_utils
from myhouse_admin.utils.utils import permission_required, PermissionRequiredMixin


logger = logging.getLogger(__name__)


class MessageListView(PermissionRequiredMixin, ListView):
    model = Message
    template_name = 'messages/message_list.html'
    permission_required = '8'
    context_object_name = "messages"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['base_layout'] = 'layout/base.html'
        return context


class MessageCreateView(PermissionRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'messages/message_create.html'
    permission_required = '8'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['load_house_sections_url'] = reverse_lazy('myhouse_admin:load_house_sections')
        context['load_section_floors_url'] = reverse_lazy('myhouse_admin:load_section_floors')
        context['load_empty_flats_url'] = reverse_lazy('myhouse_admin:load_empty_flats')
        context['load_floor_flats_url'] = reverse_lazy('myhouse_admin:load_floor_flats')
        return context

    def post(self, request, *args, **kwargs) :
        form = MessageForm(request.POST)
        form.fields['section'].queryset = Section.objects.all()
        form.fields['floor'].queryset = Floor.objects.all()
        form.fields['flat'].queryset = db_utils.get_flats()
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user.employee
            message.save()
            owners = set(db_utils.get_active_owners())
            if form.cleaned_data.get('house') is not None:
                owners = form.cleaned_data.get('house').owners
                if form.cleaned_data.get('section') is not None:
                    owners = form.cleaned_data.get('section').owners
                    if form.cleaned_data.get('floor') is not None:
                        owners = form.cleaned_data.get('floor').owners
                        if form.cleaned_data.get('flat') is not None:
                            owners = set([form.cleaned_data.get('flat').owner])
            if message.for_debtors:
                owners = {owner for owner in owners if owner.have_debts is True}
            message.recipients.set(owners)
            return redirect(reverse_lazy('myhouse_admin:message_list'))
        context = self.get_context_data()
        context['form'] = form
        return render(request, 'messages/message_create.html', context)


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@require_http_methods(['POST'])
@permission_required('3')
def message_delete_many(request):
    for message_id in request.POST.getlist('ids[]', []):
        db_utils.get_message(pk=message_id).delete()
    return JsonResponse({})


class MessageDetailView(PermissionRequiredMixin, DetailView):
    model = Message
    permission_required = '3'
    template_name = 'messages/message_detail.html'


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@require_http_methods(['DELETE'])
@permission_required('3')
def delete_message(request, pk):
    try:
        db_utils.get_message(pk=pk).delete()
    except:
        pass
    return JsonResponse({})
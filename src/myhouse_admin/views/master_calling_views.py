import logging

from django.contrib.admin.views.decorators import staff_member_required
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.urls.base import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from myhouse_admin.forms.forms import TicketForm
from myhouse_admin.models import Ticket
from myhouse_admin.utils import db_utils, utils
from myhouse_admin.utils.utils import PermissionRequiredMixin, permission_required


logger = logging.getLogger(__name__)


class TicketListView(PermissionRequiredMixin, ListView):
    model = Ticket
    template_name = 'tickets/ticket_list.html'
    context_object_name = 'tickets'
    permission_required = '9'


class TicketCreateView(PermissionRequiredMixin, CreateView):
    model = Ticket
    form_class = TicketForm
    template_name = 'tickets/ticket_create.html'
    permission_required = '9'

    def get_success_url(self) -> str:
        return reverse_lazy('myhouse_admin:master_request_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['load_owner_flats_url'] = reverse_lazy('myhouse_admin:load_owner_flats')
        return context

    def form_valid(self, form):
        ticket: Ticket = form.save(commit=False)
        if 'convenient_date' in form.cleaned_data and 'convenient_time' in form.cleaned_data:
            ticket.convenient_time = utils.get_datetime_from_date_and_time(
                form.cleaned_data['convenient_date'],
                form.cleaned_data['convenient_time'])
        ticket.save()
        return redirect(self.get_success_url())


class TicketDetailView(PermissionRequiredMixin, DetailView):
    model = Ticket
    template_name = 'tickets/ticket_detail.html'
    permission_required = '9'


class TicketUpdateView(PermissionRequiredMixin, UpdateView):
    model = Ticket
    form_class = TicketForm
    template_name = 'tickets/ticket_update.html'
    permission_required = '9'

    def get_success_url(self) -> str:
        return reverse_lazy('myhouse_admin:master_request_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['load_owner_flats_url'] = reverse_lazy('myhouse_admin:load_owner_flats')
        context['update'] = True
        return context

    def form_valid(self, form):
        ticket: Ticket = form.save(commit=False)
        if 'convenient_date' in form.cleaned_data and 'convenient_time' in form.cleaned_data:
            ticket.convenient_time = utils.get_datetime_from_date_and_time(
                form.cleaned_data['convenient_date'],
                form.cleaned_data['convenient_time'])
        ticket.save()
        return redirect(self.get_success_url())


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@require_http_methods(['DELETE'])
@permission_required('9')
def delete_ticket(request, pk):
    try:
        db_utils.delete_ticket(pk)
    except:
        pass
    return JsonResponse({})
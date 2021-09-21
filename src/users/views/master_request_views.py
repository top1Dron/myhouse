from myhouse_admin.models import Ticket
from myhouse_admin.forms.forms import OwnerTicketForm
from django.http.response import Http404, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.http import urlencode
from django.views.decorators.http import require_http_methods
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView

from myhouse_admin.utils import db_utils, utils


class OwnerRequestsDetailView(DetailView):
    template_name = 'master_calling/index.html'
    context_object_name = 'owner'

    def get_object(self):
        if 'owner_ID' in self.request.GET and hasattr(self.request.user, 'employee'):
            return db_utils.get_owner_object_by_params(ID=self.request.GET.get('owner_ID'))
        else:
            try:
                return self.request.user.owner
            except:
                raise Http404('Вы не являетесь владельцем')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['flats'] = db_utils.get_owner_flats(owner=self.get_object())
        context['owner_ID'] = None
        if 'owner_ID' in self.request.GET:
            context['owner_ID'] = self.request.GET['owner_ID']
        context['tickets'] = db_utils.get_owner_tickets(owner=self.get_object())
        return context


class OwnerRequestCreateView(CreateView):
    model = Ticket
    form_class = OwnerTicketForm
    template_name = 'master_calling/create.html'

    def get_success_url(self) -> str:
        url = reverse_lazy('users:owner_requests_list')
        if 'owner_ID' in self.request.GET:
            url += '?' + urlencode({'owner_ID': self.request.GET['owner_ID']})
        return url

    def form_valid(self, form):
        ticket: Ticket = form.save(commit=False)
        if 'convenient_date' in form.cleaned_data and 'convenient_time' in form.cleaned_data:
            ticket.convenient_time = utils.get_datetime_from_date_and_time(
                form.cleaned_data['convenient_date'],
                form.cleaned_data['convenient_time'])
        ticket.status = '1'
        ticket.save()
        return redirect(self.get_success_url())

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs(*args, **kwargs)
        if 'owner_ID' in self.request.GET:
            kwargs['owner'] = db_utils.get_owner_object_by_params(ID=self.request.GET['owner_ID'])
        else:
            kwargs['owner'] = self.request.user.owner
        return kwargs


@require_http_methods(['DELETE'])
def delete_ticket(request, pk):
    try:
        db_utils.delete_ticket(pk)
    except:
        pass
    return JsonResponse({})
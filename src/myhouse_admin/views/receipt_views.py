import logging

from django.contrib.admin.views.decorators import staff_member_required
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.urls.base import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from myhouse_admin.forms.forms import ReceiptForm
from myhouse_admin.models import Receipt
from myhouse_admin.utils import db_utils, utils


logger = logging.getLogger(__name__)


class ReceiptListView(utils.PermissionRequiredMixin, ListView):
    model = Receipt
    queryset = Receipt.objects.all().order_by('-creation_date')
    template_name = 'receipts/receipt_list.html'
    permission_required = '3'


class ReceiptCreateView(utils.PermissionRequiredMixin, CreateView):
    model = Receipt
    form_class = ReceiptForm
    template_name = 'receipts/receipt_create.html'
    permission_required = '3'

    def get_success_url(self) -> str:
        return reverse_lazy('myhouse_admin:receipt_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meters'] = db_utils.get_all_meter_readings()
        context['load_house_sections_url'] = reverse_lazy('myhouse_admin:load_house_sections')
        context['load_section_flats_url'] = reverse_lazy('myhouse_admin:load_section_flats')
        context['load_empty_flats_url'] = reverse_lazy('myhouse_admin:load_empty_flats')
        context['load_flat_details'] = reverse_lazy('myhouse_admin:load_flat_details')
        return context
    
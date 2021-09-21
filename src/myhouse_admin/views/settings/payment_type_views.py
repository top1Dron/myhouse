import logging

from django.contrib.admin.views.decorators import staff_member_required
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.urls.base import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

from myhouse_admin.forms.forms import PaymentTypeForm
from myhouse_admin.models import PaymentType
from myhouse_admin.utils import db_utils


logger = logging.getLogger(__name__)


class PaymentTypeCreateView(CreateView):
    model = PaymentType
    form_class = PaymentTypeForm
    template_name = 'settings/payment_type/payment_type_create.html'

    def get_success_url(self) -> str:
        return reverse_lazy('myhouse_admin:payment_type_list')


class PaymentTypeListView(ListView):
    model = PaymentType
    template_name = 'settings/payment_type/payment_type_list.html'
    queryset = db_utils.get_payment_types()
    context_object_name = 'payment_types'


class PaymentTypeUpdateView(UpdateView):
    model = PaymentType
    form_class = PaymentTypeForm
    template_name = 'settings/payment_type/payment_type_update.html'

    def get_success_url(self) -> str:
        return reverse_lazy('myhouse_admin:payment_type_list')


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@require_http_methods(['DELETE'])
def delete_payment_type(request, pk):
    db_utils.get_payment_type(pk=pk).delete()
    return JsonResponse({})
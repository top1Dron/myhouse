import logging

from django.contrib.admin.views.decorators import staff_member_required
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.urls.base import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from myhouse_admin.forms.forms import TariffForm, TariffServiceFormSet
from myhouse_admin.models import Tariff, TariffService
from myhouse_admin.utils import db_utils
from myhouse_admin.utils.utils import PermissionRequiredMixin, permission_required


logger = logging.getLogger(__name__)


class TariffListView(PermissionRequiredMixin, ListView):
    model = Tariff
    template_name = 'settings/tariff/tariff_list.html'
    queryset = db_utils.get_tariffs()
    context_object_name = 'tariffs'
    permission_required = '13'


class TariffCreateView(PermissionRequiredMixin, CreateView):
    model = Tariff
    form_class = TariffForm
    template_name = 'settings/tariff/tariff_create.html'
    permission_required = '13'

    def get_success_url(self) -> str:
        return reverse_lazy('myhouse_admin:tariff_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'tariff_id' in self.request.GET:
            tariff = db_utils.get_tariff(pk=self.request.GET.get('tariff_id'))
            context['form'].fields['name'].initial = tariff.name
            context['form'].fields['description'].initial = tariff.description
            initial = list(tariff.tariff_services.values('service', 'price'))
            context['service_formset'] = TariffServiceFormSet(prefix='service', queryset=TariffService.objects.none(), initial=initial)
            context['service_formset'].extra = len(initial)
            context['update'] = True
        else:
            context['service_formset'] = TariffServiceFormSet(prefix='service')
        context['get_service_unit_url'] = reverse_lazy('myhouse_admin:get_service_unit')
        return context

    def form_valid(self, form):
        self.object = form.save()
        service_formset = TariffServiceFormSet(self.request.POST, prefix='service')
        for service_form in service_formset:
            if service_form.is_valid():
                try:
                    service = service_form.cleaned_data.get('service')
                except:
                    service = None
                if service is not None and service not in self.object.services.all():
                    tariff_service = service_form.save(commit=False)
                    tariff_service.tariff = self.object
                    tariff_service.save()
        return redirect(self.get_success_url())


class TariffDetailView(PermissionRequiredMixin, DetailView):
    model = Tariff
    template_name = 'settings/tariff/tariff_detail.html'
    permission_required = '13'


class TariffUpdateView(PermissionRequiredMixin, UpdateView):
    model = Tariff
    form_class = TariffForm
    template_name = 'settings/tariff/tariff_update.html'
    permission_required = '13'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service_formset'] = TariffServiceFormSet(prefix='service', queryset=self.object.tariff_services.all())
        context['get_service_unit_url'] = reverse_lazy('myhouse_admin:get_service_unit')
        context['update'] = True
        return context

    def get_success_url(self) -> str:
        return reverse_lazy('myhouse_admin:tariff_list')

    def form_valid(self, form):
        self.object = form.save()
        service_formset = TariffServiceFormSet(self.request.POST, prefix='service', queryset=self.object.tariff_services.all())
        for service_form in service_formset:
            if service_form.is_valid():
                try:
                    service = service_form.cleaned_data.get('service')
                except:
                    service = None
                if service is not None and service not in self.object.services.all():
                    tariff_service = service_form.save(commit=False)
                    tariff_service.tariff = self.object
                    tariff_service.save()
        return redirect(self.get_success_url())


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@require_http_methods(['GET'])
def get_service_unit(request):
    try:
        unit = db_utils.get_service(pk=request.GET.get('service_pk')).unit
        unit_pk = unit.pk
        unit_name = unit.name
    except:
        unit_pk = ''
        unit_name = 'Выберите...'
    return JsonResponse({'unit_name': unit_name, 'unit_id': unit_pk})


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@require_http_methods(['GET'])
def get_tariff_service_price(request):
    try:
        price = db_utils.get_tariff_service(
            tariff=request.GET.get('tariff_pk'), 
            service=request.GET.get('service_pk')).price
    except:
        price = ''
    return JsonResponse({'service_price': price})


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@require_http_methods(['DELETE'])
@permission_required('13')
def delete_tariff(request, pk):
    db_utils.get_tariff(pk=pk).delete()
    return JsonResponse({})


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@require_http_methods(['DELETE'])
@permission_required('13')
def delete_tariff_service(request, pk, tariff_service_pk):
    db_utils.get_tariff_service(pk=tariff_service_pk).delete()
    return JsonResponse({})
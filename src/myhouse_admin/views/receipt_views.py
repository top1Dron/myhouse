import logging

from django.contrib.admin.views.decorators import staff_member_required
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.urls.base import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from myhouse_admin.forms.forms import ReceiptForm, ReceiptServiceFormSet
from myhouse_admin.models import Receipt, ReceiptService
from myhouse_admin.utils import db_utils, utils


logger = logging.getLogger(__name__)


class ReceiptListView(utils.PermissionRequiredMixin, ListView):
    model = Receipt
    queryset = Receipt.objects.all().order_by('-creation_date')
    template_name = 'receipts/receipt_list.html'
    permission_required = '3'
    context_object_name = 'receipts'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cb_state'] = db_utils.get_cashbox_state()
        context['cb_indebtedness'] = db_utils.get_indebtedness()
        context['cb_balances'] = db_utils.get_flat_balances()
        return context

    def get_queryset(self):
        queryset = Receipt.objects.all().order_by('-creation_date')
        if 'flat_id' in self.request.GET:
            queryset = queryset.filter(flat=self.request.GET['flat_id'])
        return queryset


class ReceiptDetailView(utils.PermissionRequiredMixin, DetailView):
    model = Receipt
    permission_required = '3'
    template_name = 'receipts/receipt_detail.html'


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@utils.permission_required('3')
def receipt_create_view(request):
    if request.method == 'POST':
        form = ReceiptForm(request.POST)
        service_formset = ReceiptServiceFormSet(request.POST, prefix='service')
        form.fields['section'].queryset = db_utils.get_house_sections(request.POST.get('house'))
        form.fields['flat'].queryset = db_utils.get_section_flats(request.POST.get('section'))
        if form.is_valid():
            receipt = form.save(commit=False)
            receipt.summary = float(request.POST.get('summary'))
            receipt.save()
            for service_form in service_formset:
                if service_form.is_valid() and len(service_form.cleaned_data) > 0:
                    service = service_form.save(commit=False)
                    service.unit = service_form.cleaned_data.get('unit')
                    service.service = service_form.cleaned_data.get('service')
                    service.receipt = receipt
                    service.save()
            return redirect(reverse_lazy('myhouse_admin:receipt_list'))
    form_kwargs = {}
    if 'invoice_id' in request.GET:
        form_kwargs['receipt'] = db_utils.get_receipt(pk=request.GET.get('invoice_id'))
    if 'flat_id' in request.GET:
        form_kwargs['flat'] = db_utils.get_flat(pk=request.GET.get('flat_id'))
    form = ReceiptForm(**form_kwargs)
    
    if 'invoice_id' in request.GET:
        receipt = db_utils.get_receipt(pk=request.GET.get('invoice_id'))
        initial = list(receipt.r_services.values('service', 'consumption', 'unit', 'unit_price', 'total_price'))
        service_formset = ReceiptServiceFormSet(prefix='service', queryset=ReceiptService.objects.none(), initial=initial)
        service_formset.extra = len(initial)
    else:
        service_formset = ReceiptServiceFormSet(prefix='service', queryset=ReceiptService.objects.none())
    return render(request, 'receipts/receipt_create.html', {
        'form': form,
        'service_formset': service_formset,
        'get_service_unit_url': reverse_lazy('myhouse_admin:get_service_unit'),
        'load_house_sections_url': reverse_lazy('myhouse_admin:load_house_sections'),
        'load_section_flats_url': reverse_lazy('myhouse_admin:load_section_flats'),
        'load_empty_flats_url': reverse_lazy('myhouse_admin:load_empty_flats'),
        'load_flat_details': reverse_lazy('myhouse_admin:load_flat_details'),
        'meters': db_utils.get_all_meter_readings(),
    })


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@utils.permission_required('3')
def receipt_update_view(request, pk):
    if request.method == 'POST':
        form = ReceiptForm(request.POST, instance=db_utils.get_receipt(pk=pk))
        service_formset = ReceiptServiceFormSet(request.POST, prefix='service', queryset=ReceiptService.objects.filter(receipt=form.instance))
        form.fields['section'].queryset = db_utils.get_house_sections(request.POST.get('house'))
        form.fields['flat'].queryset = db_utils.get_section_flats(request.POST.get('section'))
        if form.is_valid():
            receipt = form.save(commit=False)
            receipt.summary = float(request.POST.get('summary'))
            receipt.save()
            for service_form in service_formset:
                if service_form.is_valid() and len(service_form.cleaned_data) > 0:
                    service = service_form.save(commit=False)
                    service.unit = service_form.cleaned_data.get('unit')
                    service.service = service_form.cleaned_data.get('service')
                    service.receipt = receipt
                    service.save()
            return redirect(reverse_lazy('myhouse_admin:receipt_list'))
    form = ReceiptForm(instance=db_utils.get_receipt(pk=pk), update=True)
    service_formset = ReceiptServiceFormSet(prefix='service',
        queryset=ReceiptService.objects.filter(receipt=form.instance),
    )
    for sf in service_formset:
        sf.fields['service'].initial = sf.instance.service
        sf.fields['unit'].initial = sf.instance.unit
    return render(request, 'receipts/receipt_update.html', {
        'form': form,
        'service_formset': service_formset,
        'get_service_unit_url': reverse_lazy('myhouse_admin:get_service_unit'),
        'load_house_sections_url': reverse_lazy('myhouse_admin:load_house_sections'),
        'load_section_flats_url': reverse_lazy('myhouse_admin:load_section_flats'),
        'load_empty_flats_url': reverse_lazy('myhouse_admin:load_empty_flats'),
        'load_flat_details': reverse_lazy('myhouse_admin:load_flat_details'),
        'meters': db_utils.get_flat_meters(form.instance.flat.pk),
        'update': True
    })


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@require_http_methods(['DELETE'])
@utils.permission_required('3')
def delete_receipt_view(request, pk):
    db_utils.get_receipt(pk=pk).delete()
    return JsonResponse({})


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@require_http_methods(['POST'])
@utils.permission_required('3')
def receipt_delete_many(request):
    for receipt_id in request.POST.getlist('ids[]', []):
        db_utils.get_receipt(pk=receipt_id).delete()
    return JsonResponse({})
import logging

from django.contrib.admin.views.decorators import staff_member_required
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.urls.base import reverse_lazy
from django.views.decorators.http import require_http_methods

from myhouse_admin.forms.forms import ServiceFormSet, UnitFormSet
from myhouse_admin.utils import db_utils
from myhouse_admin.utils.utils import permission_required


logger = logging.getLogger(__name__)


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@permission_required('12')
def service_unit_view(request):
    unit_formset = UnitFormSet(request.POST or None, prefix='unit', queryset=db_utils.get_all_unit())
    service_formset = ServiceFormSet(prefix='service', queryset=db_utils.get_all_services())
    for form in service_formset:
        form.fields['unit'].initial = form.instance.unit
    if request.method == 'POST':
        service_formset = ServiceFormSet(request.POST, prefix='service', queryset=db_utils.get_all_services())
        if unit_formset.is_valid():
            unit_formset.save()
        for form in service_formset:
            if form.is_valid():
                service = form.save(commit=False)
                service.unit = form.cleaned_data.get('unit')
                service.save()
        return redirect(reverse_lazy('myhouse_admin:service_unit'))
    return render(request, 'settings/services_unit/service_unit.html', {
        'unit_formset': unit_formset, 
        'service_formset': service_formset
    })


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@permission_required('12')
@require_http_methods(['DELETE'])
def unit_delete(request, pk):
    db_utils.delete_unit(unit_pk=pk)
    return JsonResponse({})


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@permission_required('12')
@require_http_methods(['DELETE'])
def service_delete(request, pk):
    db_utils.delete_service(service_pk=pk)
    return JsonResponse({})
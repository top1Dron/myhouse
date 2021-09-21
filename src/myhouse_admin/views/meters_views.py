import logging

from django.contrib.admin.views.decorators import staff_member_required
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.urls.base import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from myhouse_admin.forms.forms import MeterReadingForm
from myhouse_admin.models import MeterReading
from myhouse_admin.utils import db_utils
from myhouse_admin.utils.utils import PermissionRequiredMixin, permission_required


logger = logging.getLogger(__name__)


class MeterListView(PermissionRequiredMixin, ListView):
    model = MeterReading
    queryset = db_utils.get_meter_list()
    context_object_name = "meters"
    template_name = 'meters/meter_list.html'
    permission_required = '10'


class MeterReadingListView(MeterListView):
    model = MeterReading
    template_name = 'meters/meter_reading_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Показания счетчиков'
        if 'flat_id' in self.request.GET:
            try:
                flat = db_utils.get_flat(pk=self.request.GET.get('flat_id'))
                context['title'] += f', кв. {flat.number}'
            except:
                pass
        return context

    def get_queryset(self):
        queryset = MeterReading.objects.all().order_by('-reading_date')
        if 'flat_id' in self.request.GET:
            queryset = queryset.filter(flat=self.request.GET.get('flat_id'))
        if 'service_id' in self.request.GET:
            queryset = queryset.filter(service=self.request.GET.get('service_id'))
        return queryset


class MeterReadingCreateView(PermissionRequiredMixin, CreateView):
    model = MeterReading
    form_class = MeterReadingForm
    template_name = 'meters/meter_reading_create.html'
    permission_required = '10'

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs(*args, **kwargs)
        if 'meter_id' in self.request.GET:
            kwargs['meter'] = db_utils.get_meter_reading(pk=self.request.GET.get('meter_id'))
        return kwargs

    def get_success_url(self) -> str:
        if 'another' in self.request.POST:
            return reverse_lazy('myhouse_admin:meter_create')
        else:
            return reverse_lazy('myhouse_admin:meter_list')
    
    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['load_house_sections_url'] = reverse_lazy('myhouse_admin:load_house_sections')
        context['load_section_flats_url'] = reverse_lazy('myhouse_admin:load_section_flats')
        context['load_empty_flats_url'] = reverse_lazy('myhouse_admin:load_empty_flats')
        return context

    def form_invalid(self, form):
        if ('number' not in form.cleaned_data
            or 'reading_date' not in form.cleaned_data
            or 'status' not in form.cleaned_data
            or 'testimony' not in form.cleaned_data
            or 'service' not in form.cleaned_data):
            return super().form_invalid(form)
        else:
            meter_reading: MeterReading = db_utils.create_meter_reading(
                number=form.cleaned_data.get('number'),
                reading_date=form.cleaned_data.get('reading_date'),
                status=form.cleaned_data.get('status'),
                testimony=form.cleaned_data.get('testimony'),
                service=form.cleaned_data.get('service'),
                flat=db_utils.get_flat(pk=self.request.POST.get('flat'))
            )
            return redirect(reverse_lazy('myhouse_admin:meter_list'))


class MeterReadingUpdateView(PermissionRequiredMixin, UpdateView):
    model = MeterReading
    form_class = MeterReadingForm
    template_name = 'meters/meter_reading_update.html'
    permission_required = '10'

    def get_success_url(self) -> str:
        if 'another' in self.request.POST:
            return reverse_lazy('myhouse_admin:meter_create')
        else:
            return reverse_lazy('myhouse_admin:meter_list')
    
    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs(*args, **kwargs)
        kwargs['flat'] = self.get_object().flat
        kwargs['update'] = True
        return kwargs
    
    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['load_house_sections_url'] = reverse_lazy('myhouse_admin:load_house_sections')
        context['load_section_flats_url'] = reverse_lazy('myhouse_admin:load_section_flats_on_update')
        context['load_empty_flats_url'] = reverse_lazy('myhouse_admin:load_empty_flats')
        context['update'] = True
        return context

    def form_invalid(self, form):
        if ('number' not in form.cleaned_data
            or 'reading_date' not in form.cleaned_data
            or 'status' not in form.cleaned_data
            or 'testimony' not in form.cleaned_data
            or 'service' not in form.cleaned_data):
            return super().form_invalid(form)
        else:
            meter_reading = self.get_object()
            meter_reading.number=form.cleaned_data.get('number')
            meter_reading.reading_date=form.cleaned_data.get('reading_date')
            meter_reading.status=form.cleaned_data.get('status')
            meter_reading.testimony=form.cleaned_data.get('testimony')
            meter_reading.service=form.cleaned_data.get('service')
            meter_reading.flat=db_utils.get_flat(pk=self.request.POST.get('flat'))
            meter_reading.save()
            return redirect(self.get_success_url())


class MeterReadingDetailView(PermissionRequiredMixin, DetailView):
    model = MeterReading
    context_object_name = "meter_reading"
    template_name = 'meters/meter_reading_detail.html'
    permission_required = '10'


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@require_http_methods(['DELETE'])
@permission_required('10')
def delete_meter_reading(request, pk):
    db_utils.get_meter_reading(pk=pk).delete()
    return JsonResponse({})
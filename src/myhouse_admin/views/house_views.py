import logging

from django.contrib.admin.views.decorators import staff_member_required
from django.forms import inlineformset_factory, formset_factory
from django.http.response import JsonResponse
from django.shortcuts import redirect
from django.urls.base import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from myhouse_admin.forms.filter_forms import EmployeeSelectForm, HouseSearchForm
from myhouse_admin.forms.forms import HouseForm, HouseSectionsForm
from myhouse_admin.models import Floor, House, Section
from myhouse_admin.utils import db_utils
from myhouse_admin.utils.utils import permission_required, PermissionRequiredMixin


logger = logging.getLogger(__name__)


class HouseListView(PermissionRequiredMixin, ListView):
    model = House
    template_name = 'houses/house_list.html'
    queryset = db_utils.get_houses()
    context_object_name = 'houses'
    permission_required = '7'

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['house_search_form'] = HouseSearchForm()
        if 'name' in self.request.GET:
            context['house_search_form'].fields['house_name_search_field'].initial = self.request.GET.get('name')
        if 'address' in self.request.GET:
            context['house_search_form'].fields['house_address_search_field'].initial = self.request.GET.get('address')
        return context

    def get_queryset(self):
        kwargs = {}
        kwargs['name'] = self.request.GET.get('name')
        kwargs['address'] = self.request.GET.get('address')
        return db_utils.get_filtered_houses(**kwargs)


class HouseCreateView(PermissionRequiredMixin, CreateView):
    model = House
    form_class = HouseForm
    template_name = 'houses/house_create.html'
    permission_required = '7'

    def get_success_url(self) -> str:
        return reverse_lazy('myhouse_admin:house_list')

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        SectionFormSet = inlineformset_factory(parent_model=House,
            model=Section,
            form=HouseSectionsForm,
            can_delete=True,
            extra=0)
        context['section_formset'] = SectionFormSet()
        context['section_formset_class'] = SectionFormSet

        EmployeeFormSet = formset_factory(EmployeeSelectForm, extra=0, can_delete=True)
        context['employee_formset'] = EmployeeFormSet(prefix='employee_set')
        context['employee_formset_class'] = EmployeeFormSet
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        self.object = form.save()
        section_formset = context['section_formset_class'](self.request.POST, instance=self.object)
        employee_formset = context['employee_formset_class'](self.request.POST, prefix='employee_set')
        for section_form in section_formset:
            if section_form.is_valid():
                if section_form.cleaned_data.get('name'):
                    section = section_form.save()
                    section.instance = self.object
                    section.save()
                    for i in range(1, section_form.cleaned_data.get('floors') + 1):
                        floor = Floor.objects.create(section=section, name=f"Этаж №{i}")
        for employee_form in employee_formset:
            if employee_form.is_valid():
                try:
                    employee = db_utils.get_employee_object_by_params(
                        pk=employee_form.cleaned_data.get('worker'))
                except:
                    employee = None
                if employee is not None and employee not in self.object.workers.all():
                    self.object.workers.add(employee)
        return redirect(self.get_success_url())


class HouseUpdateView(PermissionRequiredMixin, UpdateView):
    model = House
    form_class = HouseForm
    template_name = 'houses/house_update.html'
    permission_required = '7'

    def get_success_url(self) -> str:
        return reverse_lazy('myhouse_admin:house_list')

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        SectionFormSet = inlineformset_factory(parent_model=House,
            model=Section,
            form=HouseSectionsForm,
            can_delete=True,
            extra=0)
        context['section_formset'] = SectionFormSet(instance=self.get_object())
        context['section_formset_class'] = SectionFormSet

        EmployeeFormSet = formset_factory(EmployeeSelectForm, extra=0, can_delete=True)
        context['employee_formset'] = EmployeeFormSet(prefix='employee_set')
        context['employee_formset_class'] = EmployeeFormSet
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        self.object = form.save()
        section_formset = context['section_formset_class'](self.request.POST, instance=self.object)
        employee_formset = context['employee_formset_class'](self.request.POST, prefix='employee_set')
        for section_form in section_formset:
            if section_form.is_valid():
                if section_form.cleaned_data.get('name'):
                    section = section_form.save()
                    section.instance = self.object
                    section.save()
                    if section_form.cleaned_data.get('id') is None:
                        for i in range(1, section_form.cleaned_data.get('floors') + 1):
                            floor = Floor.objects.create(section=section, name=f"Этаж №{i}")
        deleted_sections = self.request.POST['deleted_sections'].split(' ')
        for section_pk in deleted_sections:
            try:
                section = db_utils.get_section(pk=section_pk)
                section.delete()
            except:
                pass
        for employee_form in employee_formset:
            if employee_form.is_valid():
                try:
                    employee = db_utils.get_employee_object_by_params(
                        pk=employee_form.cleaned_data.get('worker'))
                except:
                    employee = None
                if employee is not None and employee not in self.object.workers.all():
                    self.object.workers.add(employee)
        return redirect(self.get_success_url())


class HouseDetailView(PermissionRequiredMixin, DetailView):
    model = House
    template_name = 'houses/house_detail.html'
    permission_required = '7'


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@require_http_methods(['DELETE'])
@permission_required('7')
def delete_employee_from_house(request, employee_pk, house_pk):
    try:
        db_utils.delete_house_worker(employee_pk, house_pk)
    except:
        pass
    return JsonResponse({})


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@require_http_methods(['DELETE'])
@permission_required('7')
def delete_house(request, pk):
    try:
        house = db_utils.get_house_object_by_params(pk=pk)
        house.delete()
    except:
        pass
    return JsonResponse({})
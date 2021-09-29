import logging

from django.contrib.admin.views.decorators import staff_member_required
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.urls.base import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from myhouse_admin.forms.forms import FlatForm
from myhouse_admin.models import Flat, Floor, Section
from myhouse_admin.utils import db_utils
from myhouse_admin.utils.utils import permission_required, PermissionRequiredMixin


logger = logging.getLogger(__name__)


class FlatCreateView(PermissionRequiredMixin, CreateView):
    model = Flat
    form_class = FlatForm
    template_name = 'flats/flat_create.html'
    permission_required = '5'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['load_house_sections_url'] = reverse_lazy('myhouse_admin:load_house_sections')
        context['load_section_floors_url'] = reverse_lazy('myhouse_admin:load_section_floors')
        context['load_empty_flats_url'] = reverse_lazy('myhouse_admin:load_empty_flats')
        return context

    def post(self, request, *args, **kwargs):
        form = FlatForm(request.POST)
        form.fields['section'].queryset = Section.objects.all()
        form.fields['floor'].queryset = Floor.objects.all()
        if form.is_valid():
            flat = form.save()
            if form.cleaned_data.get('personal_account') is not None and flat:
                pa = db_utils.get_personal_account(
                    pk=form.cleaned_data.get('personal_account'))
                pa.flat = flat
                pa.save()
            if 'another' in self.request.POST:
                return redirect(reverse_lazy('myhouse_admin:flat_create'))
            else:
                return redirect(reverse_lazy('myhouse_admin:flat_detail', kwargs={'pk':flat.pk}))
        context = self.get_context_data()
        context['form'] = form
        return render(request, 'flats/flat_create.html', context)


class FlatDetailView(PermissionRequiredMixin, DetailView):
    model = Flat
    template_name = 'flats/flat_detail.html'
    permission_required = '5'


class FlatListView(PermissionRequiredMixin, ListView):
    model = Flat
    template_name = 'flats/flat_list.html'
    queryset = db_utils.get_flats()
    context_object_name = 'flats'
    permission_required = '5'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['has_debt'] = 0
        if 'has_debt' in self.request.GET:
            context['has_debt'] = self.request.GET['has_debt']
        return context
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if 'has_debt' in self.request.GET:
            if self.request.GET['has_debt'] == '1':
                queryset = [flat for flat in db_utils.get_flats() if flat.actual_balance < 0]
            elif self.request.GET['has_debt'] == '2':
                queryset = [flat for flat in db_utils.get_flats() if flat.actual_balance >= 0]
        return queryset


class FlatUpdateView(PermissionRequiredMixin, UpdateView):
    model = Flat
    form_class = FlatForm
    template_name = 'flats/flat_update.html'
    permission_required = '5'

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs(*args, **kwargs)
        kwargs['floor'] = self.get_object().floor
        kwargs['pa'] = self.get_object().flat_personal_account
        return kwargs

    def get_success_url(self) -> str:
        if 'another' in self.request.POST:
            return reverse_lazy('myhouse_admin:flat_create')
        else:
            return reverse_lazy('myhouse_admin:flat_detail', kwargs={'pk': self.get_object().pk})
    
    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['load_house_sections_url'] = reverse_lazy('myhouse_admin:load_house_sections')
        context['load_section_floors_url'] = reverse_lazy('myhouse_admin:load_section_floors')
        context['load_empty_flats_url'] = reverse_lazy('myhouse_admin:load_empty_flats')
        return context

    def form_invalid(self, form):
        if ('floor' not in self.request.POST
            or 'number' not in form.cleaned_data
            or 'square' not in form.cleaned_data
            or 'owner' not in form.cleaned_data
            or 'tariff' not in form.cleaned_data
            or 'personal_account' not in form.cleaned_data):
            return super().form_invalid(form)
        else:
            flat = self.get_object()
            flat.number = form.cleaned_data.get('number')
            flat.square = form.cleaned_data.get('square')
            flat.owner = form.cleaned_data.get('owner')
            flat.tariff = form.cleaned_data.get('tariff')
            flat.floor = db_utils.get_floor(pk=self.request.POST.get('floor'))
            flat.save()
            if flat:
                if form.cleaned_data.get('personal_account') is not None:
                    pa = db_utils.get_personal_account(
                        pk=form.cleaned_data.get('personal_account'))
                    pa.flat = flat
                    pa.save()
                if 'another' in self.request.POST:
                    return redirect(reverse_lazy('myhouse_admin:flat_create'))
                else:
                    return redirect(reverse_lazy('myhouse_admin:flat_detail', kwargs={'pk':flat.pk}))
            else:
                return super().form_invalid(form)


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@require_http_methods(['GET'])
def load_house_sections(request):
    sections = db_utils.get_house_sections(request.GET.get('house'))
    return render(request, 'flats/section_dropdown_list_options.html', {'sections': sections})


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@require_http_methods(['GET'])
def load_section_floors(request):
    floors = db_utils.get_section_floors(request.GET.get('section'))
    return render(request, 'flats/floor_dropdown_list_options.html', {'floors': floors})


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@require_http_methods(['GET'])
def load_section_flats_without_pa(request):
    flats = db_utils.get_section_flats_without_personal_account(request.GET.get('section'))
    return render(request, 'flats/flat_dropdown_list_options.html', {'flats': flats})


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@require_http_methods(['GET'])
def load_section_flats_on_update_pa(request):
    flats = db_utils.get_current_and_empty_flats(request.GET.get('flat'), request.GET.get('section'))
    return render(request, 'flats/flat_dropdown_list_options.html', {'flats': flats})


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@require_http_methods(['GET'])
def load_section_flats_on_update(request):
    flats = db_utils.get_current_and_selected_section_flats(request.GET.get('flat'), request.GET.get('section'))
    return render(request, 'flats/flat_dropdown_list_options.html', {'flats': flats})


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@require_http_methods(['GET'])
def load_empty_flats(request):
    flats = Flat.objects.none()
    return render(request, 'flats/flat_dropdown_list_options.html', {'flats': flats})


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@require_http_methods(['GET'])
def load_owner_flats(request):
    flats = db_utils.get_owner_flats(request.GET.get('owner'))
    return render(request, 'flats/owner_flats_list.html', {'flats': flats})


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@require_http_methods(['GET'])
def load_flat_details(request):
    try:
        flat = db_utils.get_flat(pk=request.GET.get('flat'))
    except:
        flat = None
    if flat is not None:
        owner = f'<a href="{reverse_lazy("myhouse_admin:owner_detail", kwargs={"pk": flat.owner.pk})}">{flat.owner}</a>'
        owner_phone = f'<a href="tel:{flat.owner.user.phone_number}">{flat.owner.user.phone_number}</a>'
        try:
            flat_tariff = f'<a href="{reverse_lazy("myhouse_admin:tariff_detail", kwargs={"pk": flat.tariff.pk})}" tariff_pk="{flat.tariff.pk}">{flat.tariff}</a>'
        except:
            flat_tariff = 'не выбран'
    else:
        owner = owner_phone = flat_tariff = 'не выбран'
    return JsonResponse({'flat_owner_name': owner, 'flat_owner_phone': owner_phone, 'flat_tariff': flat_tariff})


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@require_http_methods(['GET'])
def load_section_flats(request):
    flats = db_utils.get_section_flats(request.GET.get('section'))
    return render(request, 'flats/flat_dropdown_list_options.html', {'flats': flats})


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@require_http_methods(['DELETE'])
@permission_required('5')
def delete_flat(request, pk):
    try:
        db_utils.delete_flat(pk)
    except:
        pass
    return JsonResponse({})


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@require_http_methods(['GET'])
def load_floor_flats(request):
    flats = db_utils.get_floor_flats(request.GET.get('floor'))
    return render(request, 'flats/flat_dropdown_list_options.html', {'flats': flats})


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@require_http_methods(['GET'])
def load_house_flats(request):
    flats = db_utils.get_house_flats(request.GET.get('house'))
    return render(request, 'flats/flat_dropdown_list_options.html', {'flats': flats})


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@require_http_methods(['GET'])
def load_flat_meters(request):
    meters = db_utils.get_flat_meters(request.GET.get('flat'))
    return render(request, 'receipts/receipt_flat_meters.html', {'meters': meters})
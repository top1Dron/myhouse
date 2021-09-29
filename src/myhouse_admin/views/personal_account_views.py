import logging

from django.contrib.admin.views.decorators import staff_member_required
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.urls.base import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from myhouse_admin.forms.forms import PersonalAccountForm
from myhouse_admin.models import PersonalAccount
from myhouse_admin.utils import db_utils
from myhouse_admin.utils.utils import PermissionRequiredMixin, permission_required, export_models_to_excel


logger = logging.getLogger(__name__)


class PersonalAccountCreateView(PermissionRequiredMixin, CreateView):
    model = PersonalAccount
    form_class = PersonalAccountForm
    template_name = 'personal_accounts/pa_create.html'
    permission_required = '4'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['load_house_sections_url'] = reverse_lazy('myhouse_admin:load_house_sections')
        context['load_section_flats_without_pa_url'] = reverse_lazy('myhouse_admin:load_section_flats_without_pa')
        context['load_flat_details'] = reverse_lazy('myhouse_admin:load_flat_details')
        context['load_empty_flats_url'] = reverse_lazy('myhouse_admin:load_empty_flats')
        context['update'] = False
        return context

    def form_invalid(self, form):
        if ('uid' not in form.cleaned_data
            or 'status' not in form.cleaned_data):
            return super().form_invalid(form)
        else:
            pa: PersonalAccount = db_utils.create_pa(
                uid=form.cleaned_data.get('uid'),
                status=form.cleaned_data.get('status'),
            )
            if ('flat' in self.request.POST
                and 'section' in self.request.POST
                and 'house' in self.request.POST):
                pa.flat = db_utils.get_flat(pk=self.request.POST.get('flat'))
            pa.save()
            return redirect(reverse_lazy('myhouse_admin:personal_account_list'))


class PersonalAccountListView(PermissionRequiredMixin, ListView):
    model = PersonalAccount
    queryset = db_utils.get_personal_accounts()
    context_object_name = 'personal_accounts'
    template_name = 'personal_accounts/pa_list.html'
    permission_required = '4'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cb_state'] = db_utils.get_cashbox_state()
        context['cb_indebtedness'] = db_utils.get_indebtedness()
        context['cb_balances'] = db_utils.get_flat_balances()
        context['has_debt'] = 0
        if 'has_debt' in self.request.GET:
            context['has_debt'] = self.request.GET['has_debt']
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        if 'has_debt' in self.request.GET:
            if self.request.GET['has_debt'] == '1':
                queryset = [flat.personal_account for flat in db_utils.get_flats() if (flat.flat_personal_account is not None 
                    and flat.actual_balance < 0)]
            elif self.request.GET['has_debt'] == '2':
                queryset = [flat.personal_account for flat in db_utils.get_flats() if (flat.flat_personal_account is not None 
                    and flat.actual_balance >= 0)]
        return queryset


class PersonalAccountDetailView(PermissionRequiredMixin, DetailView):
    model = PersonalAccount
    template_name = 'personal_accounts/pa_detail.html'
    context_object_name = 'personal_account'
    permission_required = '4'


class PersonalAccountUpdateView(PermissionRequiredMixin, UpdateView):
    model = PersonalAccount
    form_class = PersonalAccountForm
    template_name = 'personal_accounts/pa_update.html'
    permission_required = '4'

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs(*args, **kwargs)
        kwargs['flat'] = self.get_object().flat
        return kwargs
    
    def get_success_url(self) -> str:
        return reverse_lazy('myhouse_admin:personal_account_detail', kwargs={'pk':self.get_object().pk})

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['load_house_sections_url'] = reverse_lazy('myhouse_admin:load_house_sections')
        context['load_section_flats_on_update_pa_url'] = reverse_lazy('myhouse_admin:load_section_flats_on_update_pa')
        context['load_flat_details'] = reverse_lazy('myhouse_admin:load_flat_details')
        context['load_empty_flats_url'] = reverse_lazy('myhouse_admin:load_empty_flats')
        context['update'] = True
        return context

    def form_invalid(self, form):
        if ('uid' not in form.cleaned_data
            or 'status' not in form.cleaned_data):
            return super().form_invalid(form)
        else:
            personal_account = self.get_object()
            personal_account.status = form.cleaned_data.get('status')
            personal_account.uid = form.cleaned_data.get('uid')
            personal_account.save()
            if personal_account:
                if self.request.POST.get('flat') is not None:
                    personal_account.flat = db_utils.get_flat(
                        pk=self.request.POST.get('flat'))
                    personal_account.save()
                return redirect(reverse_lazy('myhouse_admin:personal_account_detail', kwargs={'pk':personal_account.pk}))
            else:
                return super().form_invalid(form)


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@require_http_methods(['DELETE'])
@permission_required('4')
def delete_personal_account(request, pk):
    db_utils.get_personal_account(pk=pk).delete()
    return JsonResponse({})


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
def export_to_excel(request):
    return export_models_to_excel('accounts', PersonalAccount)
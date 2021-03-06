import logging

from django.contrib.admin.views.decorators import staff_member_required
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.urls.base import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from myhouse_admin.forms.forms import CashboxRecordForm
from myhouse_admin.models import CashboxRecord, PaymentType
from myhouse_admin.utils import db_utils
from myhouse_admin.utils.utils import PermissionRequiredMixin, permission_required, get_dt_now_object, export_models_to_excel


logger = logging.getLogger(__name__)


class CashboxListView(PermissionRequiredMixin, ListView):
    model = CashboxRecord
    context_object_name = 'cashbox_records'
    template_name = 'cashbox/cb_list.html'
    permission_required = '2'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sum_in'] = db_utils.get_cashbox_in()
        context['sum_out'] = db_utils.get_cashbox_out()
        context['cb_state'] = db_utils.get_cashbox_state()
        context['cb_indebtedness'] = db_utils.get_indebtedness()
        context['cb_balances'] = db_utils.get_flat_balances()
        now = get_dt_now_object()
        context['end_date'] = f'{now.day}.{now.month}.{now.year}'
        context['start_date'] = f'{now.day}.{now.month}.{now.year}'
        if 'start_date' in self.request.GET:
            context['start_date'] = '.'.join(self.request.GET['start_date'].split('-')[-1::-1])
        if 'end_date' in self.request.GET:
            context['end_date'] = '.'.join(self.request.GET['end_date'].split('-')[-1::-1])
        return context

    def get_queryset(self):
        queryset = db_utils.get_cashbox_records()
        if 'type' in self.request.GET:
            queryset = queryset.filter(payment_type__type='0' if self.request.GET['type'] == 'in' else '1')
        if 'account_id' in self.request.GET:
            queryset = queryset.filter(personal_account=self.request.GET['account_id'])
        if 'start_date' in self.request.GET:
            queryset = queryset.filter(date__gte=self.request.GET['start_date'])
        if 'end_date' in self.request.GET:
            queryset = queryset.filter(date__lte=self.request.GET['end_date'])
        return queryset


class CashboxRecordCreateView(PermissionRequiredMixin, CreateView):
    model = CashboxRecord
    form_class = CashboxRecordForm
    template_name = 'cashbox/cbr_create.html'
    permission_required = '2'

    def get_success_url(self) -> str:
        return reverse_lazy('myhouse_admin:cashbox_list')
    
    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs(*args, **kwargs)
        if 'account_id' in self.request.GET:
            kwargs['pa'] = db_utils.get_personal_account(pk=self.request.GET['account_id'])
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'cbr_id' in self.request.GET:
            cb_record = db_utils.get_cashbox_record(pk=self.request.GET.get('cbr_id'))
        else:
            cb_record = None
        if ('type' in self.request.GET and self.request.GET.get('type') == 'in' or 
            cb_record is not None and cb_record.payment_type.type == '0'):
            context['coming'] = True
            context['form'].fields['payment_type'].queryset = PaymentType.objects.filter(type='0')
            context['load_owner_accounts_url'] = reverse_lazy('myhouse_admin:load_owner_accounts')
            context['type_name'] = '??????????????????'
            context['max_sum'] = '50000'
        else:
            context['coming'] = False
            context['form'].fields['payment_type'].queryset = PaymentType.objects.filter(type='1').exclude(name="?????????????????? ??????????????????")
            context['type_name'] = '??????????????????'
            context['max_sum'] = str(db_utils.get_cashbox_state())
        if cb_record is not None:
            context['form'].fields['owner'].initial = cb_record.personal_account.flat.owner
            context['form'].fields['personal_account'].initial = cb_record.personal_account
            context['form'].fields['payment_type'].initial = cb_record.payment_type
            context['form'].fields['is_made'].initial = cb_record.is_made
            context['form'].fields['manager'].initial = cb_record.manager
            context['form'].fields['summary'].initial = cb_record.summary
            context['form'].fields['comment'].initial = cb_record.comment
        return context


class CashboxRecordUpdateView(PermissionRequiredMixin, UpdateView):
    model = CashboxRecord
    form_class = CashboxRecordForm
    template_name = 'cashbox/cbr_update.html'
    permission_required = '2'

    def get_success_url(self) -> str:
        return reverse_lazy('myhouse_admin:cashbox_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if context['form'].instance.payment_type.type == '0':
            context['coming'] = True
            context['form'].fields['payment_type'].queryset = PaymentType.objects.filter(type='0')
            context['load_owner_accounts_url'] = reverse_lazy('myhouse_admin:load_owner_accounts')
        else:
            context['coming'] = False
            context['form'].fields['payment_type'].queryset = PaymentType.objects.filter(type='1')
        context['update'] = True
        context['type_name'] = '??????????????????' if self.object.payment_type.type == '0' else '??????????????????'
        return context

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs(*args, **kwargs)
        kwargs['pa'] = self.get_object().personal_account
        kwargs['update'] = True if self.get_object() else False
        return kwargs
    
    def form_invalid(self, form):
        if ('number' in form.cleaned_data and
            'date' in form.cleaned_data and 
            'is_made' in form.cleaned_data and 
            'payment_type'  in form.cleaned_data and 
            'manager'  in form.cleaned_data and 
            'summary' in form.cleaned_data and 
            'comment' in form.cleaned_data and
            'personal_account' in self.request.POST):
            cb_record = self.get_object()
            cb_record.number = form.cleaned_data.get('number')
            cb_record.date = form.cleaned_data.get('date')
            cb_record.is_made = form.cleaned_data.get('is_made')
            cb_record.payment_type = form.cleaned_data.get('payment_type')
            cb_record.manager = form.cleaned_data.get('manager')
            cb_record.summary = form.cleaned_data.get('summary')
            cb_record.comment = form.cleaned_data.get('comment')
            cb_record.personal_account = db_utils.get_personal_account(pk=self.request.POST.get('personal_account'))
            cb_record.save()
            return redirect(self.get_success_url())
        else:
            return super().form_invalid(form)


class CashboxRecordDetailView(PermissionRequiredMixin, DetailView):
    model = CashboxRecord
    template_name = 'cashbox/cbr_detail.html'
    context_object_name = 'cashbox_record'
    permission_required = '2'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type_name'] = '??????????????????' if self.object.payment_type.type == '0' else '??????????????????'
        return context


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@require_http_methods(['GET'])
@permission_required('2')
def load_owner_accounts(request):
    accounts = db_utils.get_owner_accounts(request.GET.get('owner'))
    return render(request, 'cashbox/account_dropdown_list_options.html', {'accounts': accounts})


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@require_http_methods(['DELETE'])
@permission_required('2')
def delete_cashbox_record(request, pk):
    try:
        db_utils.delete_cashbox_record(pk)
    except:
        pass
    return JsonResponse({})


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
def export_to_excel(request):
    return export_models_to_excel('account_transactions', CashboxRecord)


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
def export_one_to_excel(request, pk):
    cb_record = db_utils.get_cashbox_record(pk=pk)
    return export_models_to_excel(f'account_transaction_{cb_record.number}', cb_record)
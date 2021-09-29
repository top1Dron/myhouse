import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http.response import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import get_template
from django.urls.base import reverse_lazy
from django.utils.http import urlencode
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from myhouse_admin.models import CashboxRecord, PaymentType, Receipt
from myhouse_admin.utils import db_utils, utils


logger = logging.getLogger(__name__)


class ReceiptListView(utils.PermissionRequiredMixin, ListView):
    model = Receipt
    queryset = Receipt.objects.all().order_by('-creation_date')
    template_name = 'cabinet_receipts/receipt_list.html'
    context_object_name = 'receipts'
    owner_cabinet = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['flats'] = db_utils.get_owner_flats(owner=self.get_object())
        context['owner_ID'] = None
        if 'owner_ID' in self.request.GET:
            context['owner_ID'] = self.request.GET['owner_ID']
        return context

    def get_object(self):
        if 'owner_ID' in self.request.GET and hasattr(self.request.user, 'employee'):
            return db_utils.get_owner_object_by_params(ID=self.request.GET.get('owner_ID'))
        else:
            try:
                return self.request.user.owner
            except:
                raise Http404('Вы не являетесь владельцем')

    def get_queryset(self):
        owner = self.get_object()
        queryset = Receipt.objects.filter(flat__owner=owner).order_by('-creation_date')
        if 'flat_id' in self.request.GET:
            queryset = queryset.filter(flat=self.request.GET['flat_id'])
        return queryset


class ReceiptDetailView(utils.PermissionRequiredMixin, DetailView):
    model = Receipt
    template_name = 'cabinet_receipts/receipt_detail.html'
    owner_cabinet = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['flats'] = db_utils.get_owner_flats(owner=self.get_owner_object())
        context['owner_ID'] = None
        if 'owner_ID' in self.request.GET:
            context['owner_ID'] = self.request.GET['owner_ID']
        return context

    def get_owner_object(self):
        if 'owner_ID' in self.request.GET and hasattr(self.request.user, 'employee'):
            return db_utils.get_owner_object_by_params(ID=self.request.GET.get('owner_ID'))
        else:
            try:
                return self.request.user.owner
            except:
                raise Http404('Вы не являетесь владельцем')


@login_required
@utils.owner_flat_required
def pay_for_receipt(request, pk):
    receipt = db_utils.get_receipt(pk=pk)
    if (receipt.status != '3' 
        and receipt.flat.balance >= receipt.summary 
        and db_utils.get_cashbox_state() >= receipt.summary):

        receipt.status = 3
        receipt.save()
        db_utils.create_cashbox_out(
            number=utils.get_auto_id(CashboxRecord),
            date=utils.get_dt_now_object(),
            is_made=True,
            payment_type=PaymentType.objects.get(name='Погашение квитанции'),
            summary=receipt.summary,
            receipt=receipt
        )
        messages.success(request, 'Квитанция успешно оплачена!')
    else:
        if receipt.status == '3':
            messages.info(request, 'Квитанция уже оплачена')
        elif receipt.flat.balance < receipt.summary:
            messages.error(request, 'У вас недостаточно средств на балансе')
        else:
            messages.error(request, "Произошли технические проблемы в системе (Не хватает средств в кассе). "
                "Пожалуйста, повторите оплату через некоторое время позже")
    url_data = {}
    if request.GET.get('owner_ID') is not None:
        url_data['owner_ID'] = request.GET.get('owner_ID')
    return redirect(reverse_lazy('users:receipt_detail', kwargs={'pk': receipt.pk}) + '?' + urlencode(url_data))


class GeneratePDF(View):
    def get(self, request, *args, **kwargs):
        template = get_template('cabinet_receipts/receipt_to_pdf.html')
        context = {
            "receipt": db_utils.get_receipt(pk=kwargs['pk']),
            "payment_details": db_utils.get_payments_details(),
        }
        html = template.render(context)
        pdf, filename = utils.render_to_pdf('cabinet_receipts/receipt_to_pdf.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            content = "inline; filename='%s'" %(filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename='%s'" %(filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")
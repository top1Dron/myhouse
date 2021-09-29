from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.urls import reverse_lazy

from myhouse_admin.utils import db_utils, utils
from myhouse_admin.utils.utils import permission_required

@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@permission_required('1')
def index(request):
    context = {}
    context['houses_count'] = db_utils.get_houses().count()
    context['active_owners_count'] = db_utils.get_all_owners().filter(user__status='2').count()
    context['active_tickets_count'] = db_utils.get_tickets_in_progress().count()
    context['flats_count'] = db_utils.get_flats().count()
    context['pa_count'] = db_utils.get_personal_accounts().count()
    context['new_tickets_count'] = db_utils.get_new_tickets().count()
    context['cb_state'] = db_utils.get_cashbox_state()
    context['cb_indebtedness'] = db_utils.get_indebtedness()
    context['cb_balances'] = db_utils.get_flat_balances()
    context['current_year'] = utils.get_dt_now_object().year
    context['indebtedness_per_year'] = db_utils.get_indebtedness_per_year(utils.get_dt_now_object().year)
    context['paid_indebtedness_per_year'] = db_utils.get_repaid_indebtedness_per_year(utils.get_dt_now_object().year)
    context['cashbox_in_per_year'] = db_utils.get_cashbox_in_per_year(utils.get_dt_now_object().year)
    context['cashbox_out_per_year'] = db_utils.get_cashbox_out_per_year(utils.get_dt_now_object().year)
    return render(request, 'statistics/statistics.html', context=context)
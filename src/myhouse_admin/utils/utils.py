from datetime import datetime as dt, date
import calendar

from django.contrib.auth.decorators import user_passes_test
from django.db.models import Model
from django.http.response import Http404
from django.shortcuts import redirect
from django.urls.base import reverse_lazy
from django.utils.functional import wraps

from . import db_utils


def get_current_datetime() -> str:
    t = dt.now()
    return f'{t:%d%m%y}'

def get_auto_id(model: Model):
    try:
        auto_id = f'{model.objects.all().order_by("-id").first().pk + 1:05d}'
    except AttributeError:
        auto_id = f'00001'
    return get_current_datetime() + auto_id

def get_dt_now_object():
    return dt.now()


def get_datetime_from_date_and_time(date, time):
    return dt.combine(date, time)


def permission_required(permission_number: str, login_url=reverse_lazy('myhouse_admin:admin_login')):
    return user_passes_test(lambda u: permission_number in u.employee.role.abilities, login_url=login_url)


class UserCheckMixin(object):
    user_check_failure_path = ''  # can be path, url name or reverse_lazy

    def check_user(self, user):
        return True
    
    def check_cabinet_user(self, request):
        return True

    def user_check_failed(self, request, *args, **kwargs):
        return redirect(self.user_check_failure_path)

    def dispatch(self, request, *args, **kwargs):
        if not self.owner_cabinet:
            if not self.check_user(request.user):
                return self.user_check_failed(request, *args, **kwargs)
        else:
            if not self.check_cabinet_user(request):
                return self.user_check_failed(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)


class PermissionRequiredMixin(UserCheckMixin):
    user_check_failure_path = reverse_lazy('myhouse_admin:admin_login')
    permission_required = None
    owner_cabinet = False

    def check_user(self, user):
        return self.permission_required in user.employee.role.abilities
    
    def check_cabinet_user(self, request):
        if 'owner_ID' in request.GET or hasattr(request.user, 'owner'):
            return True
        else:
            return False


class CabinetPermissionRequiredMixin:
    user_check_failure_path = reverse_lazy('users:login')
    
    def dispatch(self, request, *args, **kwargs):
        if 'owner_ID' in request.GET:
            return super().dispatch(request, *args, **kwargs)
        else:
            if hasattr(request.user, 'owner'):
                return super().dispatch(request, *args, **kwargs)
            else:
                return redirect(self.user_check_failure_path)


def owner_flat_required(view):
    @wraps(view)
    def inner(request, *args, **kwargs):
        user_check_failure_path = reverse_lazy('users:login')
        if 'owner_ID' in request.GET:
            owner = db_utils.get_owner_object_by_params(ID=request.GET['owner_ID'])
        else:
            if hasattr(request.user, 'owner'):
                owner = request.user.owner
            else:
                return redirect(user_check_failure_path)

        if len(owner.flats.all()) == 0:
            return redirect(user_check_failure_path)
            
        return view(request, *args, **kwargs)
    
    return inner

def get_month_range(month:str):
    _month, year = [int(i) for i in month.split('.')]
    start_day, end_day = calendar.monthrange(year, _month)
    return (date(year=year, month=_month, day=start_day), 
        date(year=year, month=_month, day=end_day))
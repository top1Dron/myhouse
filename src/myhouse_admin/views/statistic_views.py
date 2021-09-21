from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.urls import reverse_lazy

from myhouse_admin.utils.utils import permission_required

@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@permission_required('1')
def index(request):
    return render(request, 'statistics/statistics.html')
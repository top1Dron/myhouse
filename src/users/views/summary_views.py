from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.http import urlencode

from myhouse_admin.utils import db_utils
from myhouse_admin.utils.utils import owner_flat_required


@login_required
@owner_flat_required
def summary(request):
    if 'owner_ID' in request.GET:
        owner = db_utils.get_owner_object_by_params(ID=request.GET['owner_ID'])
    else:
        if hasattr(request.user, 'owner'):
            owner = request.user.owner
    if 'flat_id' not in request.GET:
        url_data = {}
        if request.GET.get('owner_ID') is not None:
            url_data['owner_ID'] = request.GET.get('owner_ID')
        url_data['flat_id'] = owner.flats.first().pk
        return redirect(reverse_lazy('users:summary') + '?' + urlencode(url_data))
    else:
        flat = db_utils.get_flat(pk=int(request.GET['flat_id']))
        flats = db_utils.get_owner_flats(owner=owner)
    
    context = {'flat': flat, 'flats': flats}
    if 'owner_ID' in request.GET:
        context['owner_ID'] = owner.ID
    return render(request, 'summary/summary.html', context=context)
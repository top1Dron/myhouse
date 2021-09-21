from django.http.response import Http404
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.http import urlencode
from django.views.generic.detail import DetailView

from myhouse_admin.utils import db_utils


class FlatTariffDetailView(DetailView):
    template_name = 'summary/tariffs.html'
    context_object_name = 'owner'
    
    def get_object(self):
        if 'owner_ID' in self.request.GET and hasattr(self.request.user, 'employee'):
            return db_utils.get_owner_object_by_params(ID=self.request.GET.get('owner_ID'))
        else:
            try:
                return self.request.user.owner
            except:
                raise Http404('Вы не являетесь владельцем')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['flats'] = db_utils.get_owner_flats(owner=self.get_object())
        context['owner_ID'] = None
        if 'owner_ID' in self.request.GET:
            context['owner_ID'] = self.request.GET['owner_ID']
        if 'flat_id' in self.request.GET:
            context['flat'] = db_utils.get_flat(pk=self.request.GET['flat_id'])
        return context

    def get(self, request, *args, **kwargs):
        if 'flat_id' not in self.request.GET:
            url_data = {}
            if self.request.GET.get('owner_ID') is not None:
                url_data['owner_ID'] = self.request.GET.get('owner_ID')
            url_data['flat_id'] = self.get_object().flats.first().pk
            return redirect(reverse_lazy('users:tariff_index') + '?' + urlencode(url_data))
        return super().get(request, *args, **kwargs)
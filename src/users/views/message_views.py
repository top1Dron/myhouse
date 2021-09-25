from django.contrib.auth.decorators import login_required
from myhouse_admin.models import Message
from django.http.response import JsonResponse, Http404
from django.shortcuts import redirect, render
from django.urls.base import reverse_lazy
from django.utils.http import urlencode

from myhouse_admin.utils import db_utils
from myhouse_admin.views.message_views import MessageListView, MessageDetailView


class CabinetMessageDetailView(MessageDetailView):
    owner_cabinet = True
    template_name = 'cabinet_messages/message_detail.html'
    context_object_name = 'message'
    
    def get_owner_object(self):
        if 'owner_ID' in self.request.GET and hasattr(self.request.user, 'employee'):
            return db_utils.get_owner_object_by_params(ID=self.request.GET.get('owner_ID'))
        else:
            try:
                return self.request.user.owner
            except:
                raise Http404('Вы не являетесь владельцем')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['flats'] = db_utils.get_owner_flats(owner=self.get_owner_object())
        context['owner_ID'] = None
        if 'owner_ID' in self.request.GET:
            context['owner_ID'] = self.get_owner_object().ID
        return context


class CabinetMessageListView(MessageListView):
    owner_cabinet = True
    template_name = 'cabinet_messages/message_list.html'
    
    def get_owner_object(self):
        if 'owner_ID' in self.request.GET and hasattr(self.request.user, 'employee'):
            return db_utils.get_owner_object_by_params(ID=self.request.GET.get('owner_ID'))
        else:
            try:
                return self.request.user.owner
            except:
                raise Http404('Вы не являетесь владельцем')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['base_layout'] = 'cabinet_layout/base.html'
        context['flats'] = db_utils.get_owner_flats(owner=self.get_owner_object())
        context['owner_ID'] = None
        if 'owner_ID' in self.request.GET:
            context['owner_ID'] = self.get_owner_object().ID
        return context

    def get_queryset(self):
        return Message.objects.filter(recipients=self.get_owner_object())


@login_required
def delete_messages(request):
    if 'owner_ID' in request.GET and hasattr(request.user, 'employee'):
        owner = db_utils.get_owner_object_by_params(ID=request.GET.get('owner_ID'))
    else:
        try:
            owner = request.user.owner
        except:
            raise Http404('Вы не являетесь владельцем')
    for message_id in request.POST.getlist('ids[]', []):
        db_utils.get_message(pk=message_id).recipients.remove(owner)
    return JsonResponse({})


login_required
def delete_message(request, pk):
    if 'owner_ID' in request.GET and hasattr(request.user, 'employee'):
        owner = db_utils.get_owner_object_by_params(ID=request.GET.get('owner_ID'))
    else:
        try:
            owner = request.user.owner
        except:
            raise Http404('Вы не являетесь владельцем')
    try:
        db_utils.get_message(pk=pk).recipients.remove(owner)
    except:
        pass
    return JsonResponse({})
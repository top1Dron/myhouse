import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import Http404
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.http import urlencode
from django.views.generic.detail import DetailView

from myhouse_admin.utils import db_utils
from myhouse_admin.views.users.owner_views import OwnerUpdateView
from users.forms import LoginForm


logger = logging.getLogger(__name__)


def cabinet_login(request):
    form = LoginForm()

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is None:
            logger.error(f'{email}, {password}')
            email = db_utils.get_owner_email_by_ID(email)
            user = authenticate(request, email=email, password=password)
        if user is not None:
            if hasattr(user, 'owner'):
                auth_login(request, user)
                remember = request.POST.get('remember_me')
                if remember is not None:
                    settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = False
                else:
                    settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = True
                redirect_to = request.POST.get('next')
                if redirect_to:
                    return redirect(redirect_to)
                return redirect(reverse_lazy('users:profile'))
            else:
                messages.error(request, 'Владельца с такими данными не найдено')
        else:
            user = db_utils.get_user_by_email(email)
            if user is None:
                messages.error(request, 'Пользователя с такими данными не найдено')
            elif user is not None and user.is_active == False:
                messages.error(request, 'Пользователь заблокирован')
            elif user is not None and user.is_active:
                messages.error(request, 'Неверный пароль')
        form = LoginForm(request.POST)
    return render(request, 'auth/cabinet_login.html', {'form': form})


class CabinetDetailView(LoginRequiredMixin, DetailView):
    template_name = 'cabinet/owner_profile.html'
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
        return context


class CabinetUpdateView(OwnerUpdateView):
    owner_cabinet = True

    def get_success_url(self) -> str:
        url = reverse_lazy('users:profile')
        if 'owner_ID' in self.request.GET:
            url += '?' + urlencode({'owner_ID': self.request.GET['owner_ID']})
        return url
    
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
        context['base_layout'] = 'cabinet_layout/base.html'
        context['flats'] = db_utils.get_owner_flats(owner=self.get_object())
        context['owner_ID'] = None
        if 'owner_ID' in self.request.GET:
            context['owner_ID'] = self.request.GET['owner_ID']
        return context
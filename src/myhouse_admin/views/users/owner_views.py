import logging
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login as auth_login
from django.http.response import JsonResponse

from django.shortcuts import redirect
from django.urls.base import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from myhouse_admin.forms.forms import OwnerForm, UserForm
from myhouse_admin.utils import db_utils
from myhouse_admin.utils.utils import permission_required, PermissionRequiredMixin
from users.models import Owner


logger = logging.getLogger(__name__)


class OwnerCreateView(PermissionRequiredMixin, CreateView):
    model = Owner
    form_class = OwnerForm
    second_form_class = UserForm
    template_name = 'users/owner_create.html'
    permission_required = '6'

    def get_success_url(self) -> str:
        return reverse_lazy('myhouse_admin:owner_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' not in context:
            context["form"] = OwnerForm()
        if 'user_form' not in context:
            context["user_form"] = UserForm()
            context["user_form"].fields['first_name'].required = True
            context["user_form"].fields['last_name'].required = True
        context['update'] = False
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        form.fields['ID'].initial = request.POST.get('ID')
        user_form = self.second_form_class(request.POST)
        user_form.update = False
        if user_form.is_valid() and form.is_valid():
            user = user_form.save()
            user_form.instance.set_password(user_form.cleaned_data['password1'])
            user_form.instance.first_name = user_form.instance.first_name + ' ' + form.cleaned_data['second_name']
            user_form.instance.save()
            owner = form.save(commit=False)
            owner.user = user
            owner.save()
            return redirect(self.get_success_url())
        else:
            self.object = None
            return self.render_to_response(self.get_context_data(form=form, user_form=user_form))


class OwnerListView(PermissionRequiredMixin, ListView):
    model = Owner
    queryset = db_utils.get_all_owners()
    context_object_name = 'users'
    template_name = 'users/owner_list.html'
    permission_required = '6'


class OwnerDetailView(PermissionRequiredMixin, DetailView):
    model = Owner
    template_name = 'users/owner_detail.html'
    permission_required = '6'


class OwnerUpdateView(PermissionRequiredMixin, UpdateView):
    model = Owner
    form_class = OwnerForm
    second_form_class = UserForm
    template_name = 'users/owner_update.html'
    permission_required = '6'


    def get_success_url(self) -> str:
        return reverse_lazy('myhouse_admin:owner_list')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' not in context:
            context["form"] = OwnerForm(instance=self.object)
        context['form'].fields['second_name'].initial = self.object.user.first_name.split()[1]
        if 'user_form' not in context:
            context["user_form"] = UserForm(instance=self.object.user, initial={
                'first_name': self.object.user.first_name.split()[0]
            })
        context['update'] = True
        context['base_layout'] = 'layout/base.html'
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(request.POST, request.FILES, instance=self.object)
        user_form = self.second_form_class(request.POST, instance=self.object.user)

        if user_form.is_valid() and form.is_valid():
            user = user_form.save()
            if len(user_form.cleaned_data['password1']) > 7:
                user_form.instance.set_password(user_form.cleaned_data['password1'])
            user_form.instance.first_name = user_form.instance.first_name + ' ' + form.cleaned_data['second_name']
            user_form.instance.save()
            owner = form.save(commit=False)
            owner.user = user
            owner.save()
            if request.user == user_form.instance:
                user = authenticate(
                    request, 
                    email=user.email,
                    password=user_form.cleaned_data['password1'])
                auth_login(request, user)
            return redirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form, user_form=user_form))


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@require_http_methods(['DELETE'])
@permission_required('6')
def delete_owner(request, pk):
    owner = db_utils.get_owner_object_by_params(pk=pk)
    owner.user.delete()
    return JsonResponse({})
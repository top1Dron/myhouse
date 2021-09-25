import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login as auth_login, logout
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods

from django.views.generic import ListView, DetailView, UpdateView, CreateView

from myhouse_admin.forms.filter_forms import EmployeeFilterForm, UserFilterForm, UserSearchForm
from myhouse_admin.forms.forms import EmployeeForm, UserForm
from myhouse_admin.models import Employee
from myhouse_admin.utils import db_utils
from myhouse_admin.utils.utils import PermissionRequiredMixin, permission_required
from users.forms import LoginForm


logger = logging.getLogger(__name__)

@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
def welcome(request):
    return render(request, 'auth/welcome_page.html')


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
def admin_logout(request):
    logout(request)
    return redirect(reverse_lazy('myhouse_admin:admin_login'))


def admin_login(request):
    form = LoginForm()

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        remember = request.POST.get('remember_me')
        if remember is not None:
            settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = False
        else:
            settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = True
        if user is not None:
            auth_login(request, user)
            if user.is_staff:
                redirect_to = request.POST.get('next')
                if redirect_to:
                    return redirect(redirect_to)
                return redirect(reverse_lazy('myhouse_admin:welcome'))
            else:
                messages.error(request, 'Вход разрешён только сотрудникам')
        else:
            user = db_utils.get_user_by_email(email)
            if user is None:
                messages.error(request, 'Пользователя с такими данными не найдено')
            elif user is not None and user.is_active == False:
                messages.error(request, 'Пользователь заблокирован')
            elif not user.is_staff:
                messages.error(request, 'Вход разрешён только сотрудникам')
            form = LoginForm(request.POST)
    return render(request, 'auth/admin_login.html', {'form': form})


class EmployeeListView(PermissionRequiredMixin, ListView):
    model = Employee
    queryset = db_utils.get_all_workers()
    context_object_name = 'users'
    template_name = 'users/worker_list.html'
    permission_required = '15'

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['employee_filter_form'] = EmployeeFilterForm()
        context['user_filter_form'] = UserFilterForm()
        context['user_search_form'] = UserSearchForm()
        if 'role' in self.request.GET:
            context['employee_filter_form'].fields['role'].initial = self.request.GET.get('role')
            context['filtered_role'] = '1'
        if 'status' in self.request.GET:
            context['user_filter_form'].fields['status'].initial = self.request.GET.get('status')
            context['filtered_status'] = '1'
        if 'full_name' in self.request.GET:
            context['user_search_form'].fields['full_name_search_field'].initial = self.request.GET.get('full_name')
        if 'phone_number' in self.request.GET:
            context['user_search_form'].fields['phone_number_search_field'].initial = self.request.GET.get('phone_number')
        if 'email' in self.request.GET:
            context['user_search_form'].fields['email_search_field'].initial = self.request.GET.get('email')
        return context

    def get_queryset(self):
        kwargs = {}
        kwargs['role'] = self.request.GET.get('role')
        kwargs['status'] = self.request.GET.get('status')
        kwargs['full_name'] = self.request.GET.get('full_name')
        kwargs['phone_number'] = self.request.GET.get('phone_number')
        kwargs['email'] = self.request.GET.get('email')
        return db_utils.get_filtered_workers(**kwargs)


class EmployeeDetailView(PermissionRequiredMixin, DetailView):
    model = Employee
    template_name = 'users/worker_detail.html'
    context_object_name = 'employee'
    permission_required = '15'


class EmployeeUpdateView(PermissionRequiredMixin, UpdateView):
    model = Employee
    form_class = EmployeeForm
    second_form_class = UserForm
    template_name = 'users/worker_form.html'
    context_object_name = 'employee'
    permission_required = '15'

    def get_success_url(self) -> str:
        return reverse_lazy('myhouse_admin:worker_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' not in context:
            context["form"] = EmployeeForm(instance=self.object)
        if 'user_form' not in context:
            context["user_form"] = UserForm(instance=self.object.user)
        context['update'] = True
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(request.POST, instance=self.object)
        user_form = self.second_form_class(request.POST, instance=self.object.user)
        if user_form.is_valid() and form.is_valid():
            user = user_form.save()
            if len(user_form.cleaned_data['password1']) > 7:
                user_form.instance.set_password(user_form.cleaned_data['password1'])
            user_form.instance.save()
            employee = form.save(commit=False)
            employee.user = user
            employee.save()
            if request.user == user_form.instance:
                user = authenticate(
                    request, 
                    email=user.email,
                    password=user_form.cleaned_data['password1'])
                auth_login(request, user)
            return redirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form, user_form=user_form))


class EmployeeCreateView(PermissionRequiredMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    second_form_class = UserForm
    template_name = 'users/worker_form.html'
    permission_required = '15'

    def get_success_url(self) -> str:
        return reverse_lazy('myhouse_admin:worker_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' not in context:
            context["form"] = EmployeeForm()
        if 'user_form' not in context:
            context["user_form"] = UserForm()
        context['update'] = False
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        user_form = self.second_form_class(request.POST)
        user_form.update = False
        if user_form.is_valid() and form.is_valid():
            user = user_form.save()
            user.is_staff = True
            user_form.instance.set_password(user_form.cleaned_data['password1'])
            user_form.instance.save()
            employee = form.save(commit=False)
            employee.user = user
            employee.save()
            return redirect(self.get_success_url())
        else:
            self.object = None
            return self.render_to_response(self.get_context_data(form=form, user_form=user_form))
    

@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@require_http_methods(['DELETE'])
@permission_required('15')
def delete_employee(request, pk):
    employee = db_utils.get_employee_object_by_params(pk=pk)
    employee.user.status = '0'
    employee.user.save()
    return JsonResponse({})
    

@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@require_http_methods(['GET'])
@permission_required('15')
def get_employee_role(request, pk):
    try:
        worker = db_utils.get_employee_object_by_params(pk=pk)
    except:
        worker = None
    role = worker.role.name if worker is not None else ''
    return JsonResponse({'role': role})
    
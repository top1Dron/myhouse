from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from myhouse_admin.forms.forms import RoleForm, PaymentDetailsForm
from myhouse_admin.models import PaymentDetails
from myhouse_admin.utils import db_utils
from myhouse_admin.utils.utils import permission_required
from myhouse_admin.views.site_management.process_singleton import ProcessSingletonModel


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@permission_required('14')
def roles(request):
    roles = db_utils.get_roles()
    role_forms = [RoleForm(instance=role, prefix=f'{i}') for i, role in enumerate(roles)]
    if request.method == 'POST':
        role_forms = [RoleForm(request.POST, instance=role, prefix=f'{i}') for i, role in enumerate(roles)]
        role_forms_valid = [form.is_valid() for form in role_forms]
        if all(role_forms_valid):
            for role_form in role_forms:
                role_form.save()
            return redirect(reverse_lazy('myhouse_admin:roles'))
    return render(request, 'settings/roles.html', {'roles': role_forms})


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@permission_required('16')
def payment_details(request):
    process_singleton_model = ProcessSingletonModel(
        model=PaymentDetails, 
        form_class=PaymentDetailsForm,
        template_name='site_management/payment_details.html',
        success_url=reverse_lazy('myhouse_admin:payment_details'),
        request=request)
    
    redirect_available, form = process_singleton_model.get_filled_forms(
        post_dict=request.POST,
        method=request.method
    )
    if redirect_available:
        return redirect(reverse_lazy('myhouse_admin:payment_details'))
    else:
        return render(request, 'settings/payment_details.html', {
            'form': form
        })
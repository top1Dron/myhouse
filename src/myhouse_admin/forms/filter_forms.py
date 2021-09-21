from django import forms

from myhouse_admin.utils import db_utils
from users.models import Employee, User


class EmployeeFilterForm(forms.ModelForm):
    role_choices = [(role.pk, role.name) for role in db_utils.get_roles()]
    role = forms.ChoiceField(choices=tuple(role_choices))
    
    class Meta:
        model = Employee
        fields = ['role']


class UserFilterForm(forms.ModelForm):
    status_choices = list(User.USER_STATUSES)
    status = forms.ChoiceField(choices=tuple(status_choices))

    class Meta:
        model = User
        fields = ['status']


class UserSearchForm(forms.Form):
    full_name_search_field = forms.CharField(
        max_length=255, 
        required=False,
        widget=forms.widgets.Input(attrs={
            'name': 'searchFullName',
            'type': 'text',
        })
    )
    phone_number_search_field = forms.CharField(
        max_length=255, 
        required=False,
        widget=forms.widgets.Input(attrs={
            'name': 'searchPhoneNumber',
            'type': 'text',
        })
    )
    email_search_field = forms.CharField(
        max_length=255, 
        required=False,
        widget=forms.widgets.Input(attrs={
            'name': 'searchEmail',
            'type': 'text',
        })
    )


class HouseSearchForm(forms.Form):
    house_name_search_field = forms.CharField(
        max_length=255, 
        required=False,
        widget=forms.widgets.Input(attrs={
            'name': 'searchName',
            'type': 'text',
        })
    )
    house_address_search_field = forms.CharField(
        max_length=255, 
        required=False,
        widget=forms.widgets.Input(attrs={
            'name': 'searchAddress',
            'type': 'text',
        })
    )


class EmployeeSelectForm(forms.Form):
    workers = db_utils.get_all_workers()
    worker_choices = [(worker.id, worker.user.get_full_name) for worker in workers]
    worker_choices.insert(0, (0, 'Выберите'))
    worker = forms.ChoiceField(choices=worker_choices, required=True)
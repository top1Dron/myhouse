from django import forms
from django.forms.models import modelformset_factory
from django.forms.utils import to_current_timezone

from myhouse_admin.models import (CashboxRecord, Flat, Floor, House, MainPage, MeterReading, PaymentDetails, PaymentType, PersonalAccount, Receipt, Section, Service, ServicesPage, Tariff, 
    TariffPage, ContactsPage, AboutUsPage, AboutUsPageImage, AboutUsPageAdditionalImage, TariffService, Ticket, Unit)
from myhouse_admin.utils import db_utils
from myhouse_admin.utils.utils import get_auto_id, get_current_datetime, get_dt_now_object
from users.models import Employee, Owner, Role, User

class RoleForm(forms.ModelForm):
    abilities = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=Role.ABILITIES
    )
    
    class Meta:
        model = Role
        fields = ('abilities',)


class UserForm(forms.ModelForm):
    password1 = forms.CharField(label=('Пароль'), max_length=250, required=False)
    password2 = forms.CharField(label=('Повторить пароль'), max_length=250, required=False)
    update = True

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'status')

    def clean_password2(self):
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if not self.update or (self.update and password1):
            if password1 != password2:
                raise forms.ValidationError('Пароли не совпадают!')
            if len(password1) < 8:
                raise forms.ValidationError('Пароль должен быть не менее 8 символов!')
            if not any(c.isupper() for c in password1):
                raise forms.ValidationError('Пароль должен содержать хотя бы 1 символ в верхнем регистре!')
            if not any(c.islower() for c in password1):
                raise forms.ValidationError('Пароль должен содержать хотя бы 1 символ в нижнем регистре!')
            if not any(c.isdigit() for c in password1):
                raise forms.ValidationError('Пароль должен содержать хотя бы 1 цифру!')
        return super().clean()


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ('role',)


class OwnerForm(forms.ModelForm):
    second_name = forms.CharField(max_length=50)

    class Meta:
        model = Owner
        fields = ('birth_date', 'avatar', 'ID', 'about', 'viber', 'telegram')

    def clean_ID(self):
        ID = self.cleaned_data.get('ID')
        try:
            int(ID)
        except:
            raise forms.ValidationError('ID должно быть числом')
        return ID


class MainPageForm(forms.ModelForm):
    class Meta:
        model = MainPage
        fields = tuple([field.name for field in MainPage._meta.fields if field.name != 'id'])


class PaymentDetailsForm(forms.ModelForm):
    class Meta:
        model = PaymentDetails
        fields = tuple([field.name for field in PaymentDetails._meta.fields if field.name != 'id'])


class ServicesPageForm(forms.ModelForm):
    class Meta:
        model = ServicesPage
        fields = tuple([field.name for field in ServicesPage._meta.fields if field.name != 'id'])


class TariffPageForm(forms.ModelForm):
    class Meta:
        model = TariffPage
        fields = tuple([field.name for field in TariffPage._meta.fields if field.name != 'id'])


class ContactsPageForm(forms.ModelForm):
    class Meta:
        model = ContactsPage
        fields = tuple([field.name for field in ContactsPage._meta.fields if field.name != 'id'])


class AboutUsPageForm(forms.ModelForm):
    class Meta:
        model = AboutUsPage
        fields = tuple([field.name for field in AboutUsPage._meta.fields if field.name != 'id'])


class AboutUsPageImageForm(forms.ModelForm):
    class Meta:
        model = AboutUsPageImage
        fields = 'image',


class AboutUsPageAdditionalImageForm(forms.ModelForm):
    class Meta:
        model = AboutUsPageAdditionalImage
        fields = 'image',


class HouseForm(forms.ModelForm):
    class Meta:
        model = House
        fields = 'name', 'address', 'image1', 'image2', 'image3', 'image4', 'image5'


class HouseSectionsForm(forms.ModelForm):
    floors = forms.IntegerField(min_value=1)

    class Meta:
        model = Section
        fields = 'name',


class FlatForm(forms.ModelForm):
    house = forms.ModelChoiceField(queryset=db_utils.get_houses(), empty_label='Выберите...')
    section = forms.ModelChoiceField(queryset=Section.objects.none(), empty_label='Выберите...')
    floor = forms.ModelChoiceField(queryset=Floor.objects.none(), empty_label='Выберите...')
    owner = forms.ModelChoiceField(queryset=db_utils.get_all_owners(), empty_label='Выберите...')
    personal_account = forms.ModelChoiceField(queryset=db_utils.get_empty_personal_accounts(), required=False, empty_label='Выберите...')
    tariff = forms.ModelChoiceField(queryset=db_utils.get_tariffs(), required=False, empty_label='Выберите...')

    class Meta:
        model = Flat
        fields = ('number', 'square', 'floor', 'owner', 'tariff')

    def __init__(self, *args, **kwargs):
        floor = kwargs.pop('floor', None)
        super().__init__(*args, **kwargs)
        if floor:
            self.fields['house'].initial = floor.section.house
            self.fields['section'].queryset = db_utils.get_house_sections(floor.section.house.pk)
            self.fields['section'].initial = floor.section
            self.fields['floor'].queryset = db_utils.get_section_floors(floor.section.pk)
            self.fields['floor'].initial = floor


UnitFormSet = modelformset_factory(Unit, fields=('name',), extra=0, can_delete=True)


class ServiceForm(forms.ModelForm):
    unit = forms.ModelChoiceField(queryset=db_utils.get_all_unit(), empty_label='Выберите...')

    class Meta:
        model = Service
        fields = ('name', 'in_meter')


ServiceFormSet = modelformset_factory(Service, ServiceForm, extra=0, can_delete=True)


class TariffForm(forms.ModelForm):
    class Meta:
        model = Tariff
        fields = ('name', 'description')


class TariffServiceForm(forms.ModelForm):
    service = forms.ModelChoiceField(queryset=db_utils.get_all_services(), empty_label='Выберите...')
    
    class Meta:
        model = TariffService
        fields = ('service', 'price')

TariffServiceFormSet = modelformset_factory(TariffService, TariffServiceForm, fields=('service', 'price'), extra=0, can_delete=True)


class PaymentTypeForm(forms.ModelForm):
    type = forms.ChoiceField(widget=forms.Select(), choices=PaymentType.TYPES, initial=['0'])

    class Meta:
        model = PaymentType
        fields = ('name', 'type')


class PersonalAccountForm(forms.ModelForm):
    status = forms.ChoiceField(choices=PersonalAccount.STATUSES, initial='1')
    house = forms.ModelChoiceField(queryset=db_utils.get_houses(), empty_label='Выберите...')
    section = forms.ModelChoiceField(queryset=Section.objects.none(), empty_label='Выберите...')
    flat = forms.ModelChoiceField(queryset=Flat.objects.none(), empty_label='Выберите...')
    
    class Meta:
        model = PersonalAccount
        fields = ('uid', 'flat', 'status')

    def __init__(self, *args, **kwargs):
        flat = kwargs.pop('flat', None)
        super().__init__(*args, **kwargs)
        self.fields['uid'].initial = get_auto_id(PersonalAccount)
        if flat:
            self.fields['house'].initial = flat.floor.section.house
            self.fields['section'].queryset = db_utils.get_house_sections(flat.floor.section.house.pk)
            self.fields['section'].initial = flat.floor.section
            self.fields['flat'].queryset = db_utils.get_current_and_empty_flats(flat.pk, flat.floor.section.pk)
            self.fields['flat'].initial = flat


class CashboxRecordForm(forms.ModelForm):
    owner = forms.ModelChoiceField(queryset=db_utils.get_all_owners(), empty_label='Выберите...', required=False)
    personal_account = forms.ModelChoiceField(queryset=db_utils.get_personal_accounts(), empty_label='Выберите...', required=False)
    manager = forms.ModelChoiceField(queryset=db_utils.get_all_workers(), empty_label='Выберите...', required=False)
    payment_type = forms.ModelChoiceField(queryset=PaymentType.objects.all(), empty_label='Выберите...', required=False)
    
    class Meta:
        model = CashboxRecord
        fields = ('number', 'date', 'is_made', 'payment_type', 'personal_account', 'manager', 'summary', 'comment')
        
    def __init__(self, *args, **kwargs):
        pa = kwargs.pop('pa', None)
        update = kwargs.pop('update', None)
        super().__init__(*args, **kwargs)
        self.fields['number'].initial = get_auto_id(CashboxRecord)
        if not update:
            self.fields['date'].initial = get_dt_now_object()
        if pa:
            self.fields['owner'].initial = pa.flat.owner
            self.fields['personal_account'].queryset = PersonalAccount.objects.filter(pk=pa.pk)
            self.fields['personal_account'].initial = pa


class MeterReadingForm(forms.ModelForm):
    house = forms.ModelChoiceField(queryset=db_utils.get_houses(), empty_label='Выберите...')
    section = forms.ModelChoiceField(queryset=Section.objects.none(), empty_label='Выберите...')
    flat = forms.ModelChoiceField(queryset=Flat.objects.none(), empty_label='Выберите...')

    class Meta:
        model = MeterReading
        fields = ('number', 'reading_date', 'flat', 'status', 'service', 'testimony')

    def __init__(self, *args, **kwargs):
        update = kwargs.pop('update', None)
        flat = kwargs.pop('flat', None)
        meter = kwargs.pop('meter', None)
        super().__init__(*args, **kwargs)
        self.fields['service'].queryset = db_utils.get_services_in_meter()
        self.fields['service'].empty_label = 'Выберите...'
        if not update:
            self.fields['number'].initial = get_auto_id(MeterReading)
            self.fields['reading_date'].initial = get_dt_now_object()
            self.fields['status'].initial = '1'
        if flat:
            self.fields['house'].initial = flat.floor.section.house
            self.fields['section'].queryset = db_utils.get_house_sections(flat.floor.section.house.pk)
            self.fields['section'].initial = flat.floor.section
            self.fields['flat'].queryset = db_utils.get_current_and_empty_flats(flat.pk, flat.floor.section.pk)
            self.fields['flat'].initial = flat
        if meter:
            self.fields['status'].initial = meter.status
            self.fields['house'].initial = meter.flat.floor.section.house
            self.fields['section'].queryset = db_utils.get_house_sections(meter.flat.floor.section.house.pk)
            self.fields['section'].initial = meter.flat.floor.section
            self.fields['flat'].queryset = db_utils.get_current_and_empty_flats(meter.flat.pk, meter.flat.floor.section.pk)
            self.fields['flat'].initial = meter.flat
            self.fields['testimony'].initial = meter.testimony
            self.fields['service'].initial = meter.service


class ReceiptForm(forms.ModelForm):
    house = forms.ModelChoiceField(queryset=db_utils.get_houses(), empty_label='Выберите...', required=False)
    section = forms.ModelChoiceField(queryset=Section.objects.none(), empty_label='Выберите...', required=False)
    flat = forms.ModelChoiceField(queryset=Flat.objects.none(), empty_label='Выберите...', required=False)
    personal_account = forms.CharField(max_length=50, required=False)

    class Meta:
        model = Receipt
        fields = ('number', 'is_made', 'creation_date', 'start_date', 'end_date', 'flat', 'status')

    def __init__(self, *args, **kwargs):
        flat = kwargs.pop('flat', None)
        update = kwargs.pop('update', None)
        super().__init__(*args, **kwargs)
        if not update:
            self.fields['number'].initial = get_auto_id(Receipt)
            self.fields['creation_date'].initial = get_dt_now_object()
            self.fields['start_date'].initial = get_dt_now_object()
            self.fields['end_date'].initial = get_dt_now_object()


class FlatChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, flat) -> str:
        return f'{flat.number}, {flat.floor.section.house}'


class TicketForm(forms.ModelForm):
    owner = forms.ModelChoiceField(queryset=db_utils.get_all_owners(), empty_label='Выберите...', required=False)
    flat = FlatChoiceField(queryset=db_utils.get_flats(), empty_label='Выберите...')
    master_type = forms.ModelChoiceField(queryset=db_utils.get_roles(), empty_label='Любой специалист', required=False)
    master = forms.ModelChoiceField(queryset=db_utils.get_all_workers(), empty_label='Выберите...', required=False)
    convenient_date = forms.DateField(input_formats=("%d.%m.%Y",), required=False, initial=get_dt_now_object())
    convenient_time = forms.TimeField(input_formats=("%H:%M",), required=False, initial=get_dt_now_object())

    class Meta:
        model = Ticket
        fields = ('master_type', 'description', 'status', 'master', 'flat', 'comment')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].initial = '1'
        self.fields['status'].empty_label = 'Выберите...'
        if self.instance.pk is not None:
            self.fields['owner'].initial = self.instance.flat.owner.pk
            self.fields['convenient_date'].initial = to_current_timezone(self.instance.convenient_time)
            self.fields['convenient_time'].initial = to_current_timezone(self.instance.convenient_time)
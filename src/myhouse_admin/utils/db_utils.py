from typing import Iterable, Optional
import logging

from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db.models.aggregates import Sum
from django.shortcuts import get_object_or_404

from myhouse_admin.models import Block, AboutUsPageImage, AboutUsPageAdditionalImage, CashboxRecord, Flat, Floor, House, Message, MeterReading, PaymentType, Receipt, ReceiptService, Section, PersonalAccount, Service, Tariff, TariffService, Ticket, Unit
from users.models import Employee, Role, User, Owner 


logger = logging.getLogger(__name__)


def get_roles() -> Iterable[Role]:
    return Role.objects.all()


def get_all_workers() -> Iterable[Employee]:
    return Employee.objects.all().select_related('role')


def get_all_owners() -> Iterable[Owner]:
    return Owner.objects.all()


def get_active_owners() -> Iterable[Owner]:
    return get_all_owners().filter(user__status__in=['1', '2'])


def get_new_owners() -> Iterable[Owner]:
    return get_all_owners().filter(user__status='1')


def get_owners_choices() -> tuple[int, str]:
    result = [(None, 'Выберите...')]
    for owner in get_all_owners():
        result.append((owner.pk, f'{owner.user.last_name} {owner.user.first_name}'))
    return tuple(result)


def get_owner_flats(owner) -> Iterable[Flat]:
    return Flat.objects.filter(owner=owner)


def get_empty_personal_accounts() -> Iterable[PersonalAccount]:
    return PersonalAccount.objects.filter(flat=None)


def get_empty_personal_accounts_choices() -> tuple[int, str]:
    result = [(None, 'Выберите...')]
    for pa in get_empty_personal_accounts():
        result.append((pa.pk, pa.uid))
    return tuple(result)


def get_tariffs() -> Iterable[Tariff]:
    return Tariff.objects.all()


def get_tarriff_choices() -> tuple[int, str]:
    result = [(None, 'Выберите...')]
    for tariff in get_tariffs():
        result.append((tariff.pk, tariff.name))
    return tuple(result)


def get_payment_types() -> Iterable[PaymentType]:
    return PaymentType.objects.all()


def get_employee_object_by_params(**kwargs) -> Employee:
    return get_object_or_404(Employee, **kwargs)


def get_owner_object_by_params(**kwargs) -> Owner:
    return get_object_or_404(Owner, **kwargs)


def get_house_object_by_params(**kwargs) -> House:
    return get_object_or_404(House, **kwargs)


def get_section(**kwargs) -> Section:
    return get_object_or_404(Section, **kwargs)


def get_floor(**kwargs) -> Floor:
    return get_object_or_404(Floor, **kwargs)


def get_flat(**kwargs) -> Flat:
    return get_object_or_404(Flat, **kwargs)


def get_personal_account(**kwargs) -> PersonalAccount:
    return get_object_or_404(PersonalAccount, **kwargs)


def get_unit(**kwargs) -> Unit:
    return get_object_or_404(Unit, **kwargs)

def get_service(**kwargs) -> Service:
    return get_object_or_404(Service, **kwargs)


def get_tariff(**kwargs) -> Tariff:
    return get_object_or_404(Tariff, **kwargs)


def get_tariff_service(**kwargs) -> TariffService:
    return get_object_or_404(TariffService, **kwargs)


def get_payment_type(**kwargs) -> PaymentType:
    return get_object_or_404(PaymentType, **kwargs)


def get_cashbox_record(**kwargs) -> CashboxRecord:
    return get_object_or_404(CashboxRecord, **kwargs)


def get_meter_reading(**kwargs) -> MeterReading:
    return get_object_or_404(MeterReading, **kwargs)


def get_ticket(**kwargs) -> Ticket:
    return get_object_or_404(Ticket, **kwargs)


def get_receipt(**kwargs) -> Receipt:
    return get_object_or_404(Receipt, **kwargs)


def get_message(**kwargs) -> Message:
    return get_object_or_404(Message, **kwargs)


def delete_house_worker(employee_pk: int, house_pk: int) -> None:
    employee = get_employee_object_by_params(pk=employee_pk)
    house = get_house_object_by_params(pk=house_pk)
    house.workers.remove(employee)


def get_filtered_workers(queryset: Optional[Iterable[Employee]]=None, 
    role: Optional[str]=None, status: Optional[str]=None, 
    full_name: Optional[str]=None, phone_number: Optional[str]=None, email: Optional[str]=None) -> Iterable[Employee]:
    '''
    return Queryset with workers that respond given parameters
    '''

    if queryset is None:
        queryset = get_all_workers()
    if role is not None:
        roles = dict([(str(role.pk), role.name) for role in get_roles()])
        queryset = queryset.filter(role__name=roles.get(role))
    if status is not None:
        queryset = queryset.filter(user__status=status)
    if full_name is not None:
        for token in full_name.split():
            queryset = queryset.filter(Q(user__first_name__icontains=token) |
                Q(user__last_name__icontains=token))
    if phone_number is not None:
        queryset = queryset.filter(user__phone_number__icontains=phone_number.strip())
    if email is not None:
        queryset = queryset.filter(user__email__icontains=email)
    return queryset


def get_filtered_houses(queryset: Optional[Iterable[House]]=None, 
    name: Optional[str]=None, address: Optional[str]=None):
    if queryset is None:
        queryset = get_houses()
    if name is not None:
        queryset = queryset.filter(name__icontains=name)
    if address is not None:
        queryset = queryset.filter(address__icontains=address)
    return queryset


def get_user_by_email(email) -> Optional[User]:
    try:
        user = User.objects.get(email=email)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    return user


def get_owner_email_by_ID(ID: str) -> Optional[str]:
    try:
        owner = Owner.objects.get(ID=ID)
        email = owner.user.email
    except(TypeError, ValueError, OverflowError, Owner.DoesNotExist):
        email = None
    return email


def get_block_by_params(**kwargs) -> Block:
    return get_object_or_404(Block, **kwargs)


def get_image_by_params(**kwargs) -> AboutUsPageImage:
    return get_object_or_404(AboutUsPageImage, **kwargs)


def get_ad_image_by_params(**kwargs) -> AboutUsPageAdditionalImage:
    return get_object_or_404(AboutUsPageAdditionalImage, **kwargs)


def get_houses() -> Iterable[House]:
    return House.objects.all()


def get_houses_choices() -> tuple[int, str]:
    result = [(None, 'Выберите...')]
    for house in get_houses():
        result.append((house.pk, house.name))
    return tuple(result)


def get_house_sections(house_id) -> Iterable[Section]:
    try:
        return Section.objects.filter(house=house_id).order_by("name")    
    except:
        return Section.objects.none()


def get_section_floors(section_id) -> Iterable[Floor]:
    try:
        return Floor.objects.filter(section=section_id)
    except:
        return Floor.objects.none()


def get_section_flats_without_personal_account(section_id) -> Iterable[Flat]:
    try:
        return Flat.objects.filter(floor__section=section_id, personal_account=None)
    except:
        return Flat.objects.none()


def get_section_flats(section_id) -> Iterable[Flat]:
    try:
        return Flat.objects.filter(floor__section=section_id)
    except:
        return Flat.objects.none()

def get_floor_flats(floor_id) -> Iterable[Flat]:
    return Flat.objects.filter(floor=floor_id)


def get_house_flats(house_id) -> Iterable[Flat]:
    return Flat.objects.filter(floor__section__house=house_id)


def get_current_and_empty_flats(flat_id, section_id) -> Iterable[Flat]:
    return Flat.objects.filter(
        Q(pk=flat_id) |
        Q(pk__in=(flat.id for flat in get_section_flats_without_personal_account(section_id))))


def get_current_and_selected_section_flats(flat_id, section_id) -> Iterable[Flat]:
    return Flat.objects.filter(
        Q(pk=flat_id) |
        Q(pk__in=(flat.id for flat in get_section_flats(section_id))))


def create_flat(**kwargs) -> Flat:
    if kwargs['number'] and kwargs['floor'].section:
        if Flat.objects.filter(
            number=kwargs['number'], 
            floor=kwargs['floor'], 
            floor__section=kwargs['floor'].section).exists():
            return None
        else:
            return Flat.objects.create(**kwargs)


def create_pa(**kwargs) -> PersonalAccount:
    return PersonalAccount.objects.create(**kwargs)


def create_meter_reading(**kwargs) -> MeterReading:
    return MeterReading.objects.create(**kwargs)


def get_flats() -> Iterable[Flat]:
    return Flat.objects.all()


def get_all_unit() -> Iterable[Unit]:
    return Unit.objects.all()


def get_all_services() -> Iterable[Service]:
    return Service.objects.all()


def delete_unit(unit_pk) -> None:
    unit = get_unit(pk=unit_pk)
    unit.delete()


def delete_service(service_pk) -> None:
    service = get_service(pk=service_pk)
    service.delete()


def get_personal_accounts() -> Iterable[PersonalAccount]:
    return PersonalAccount.objects.all()


def get_cashbox_records() -> Iterable[CashboxRecord]:
    return CashboxRecord.objects.all()


def get_cashbox_in() -> float:
    return CashboxRecord.objects.filter(payment_type__type='0') \
        .aggregate(Sum('summary'))['summary__sum']


def get_cashbox_out() -> float:
    return CashboxRecord.objects.filter(payment_type__type='1') \
        .aggregate(Sum('summary'))['summary__sum']


def get_cashbox_state() -> float:
    return get_cashbox_in() - get_cashbox_out()


def get_owner_accounts(owner_id: int) -> Iterable[PersonalAccount]:
    try:
        return PersonalAccount.objects.filter(flat__owner__pk=owner_id)
    except:
        return get_personal_accounts()


def delete_cashbox_record(cbr_pk:int) -> None:
    get_cashbox_record(pk=cbr_pk).delete()


def delete_flat(flat_pk:int) -> None:
    get_flat(pk=flat_pk).delete()


def get_meter_list() -> Iterable[MeterReading]:
    return MeterReading.objects.all().order_by('service', 'flat', '-reading_date', '-testimony').distinct('service', 'flat')


def get_all_meter_readings() -> Iterable[MeterReading]:
    return MeterReading.objects.all().order_by('-reading_date')


def get_flat_meters(flat_id) -> Iterable[MeterReading]:
    return get_all_meter_readings().filter(flat=flat_id)


def get_services_in_meter() -> Iterable[Service]:
    return Service.objects.filter(in_meter=True)


def delete_ticket(ticket_pk)-> None:
    get_ticket(pk=ticket_pk).delete()


def get_owner_tickets(owner: Owner) -> Iterable[Ticket]:
    return Ticket.objects.filter(flat__in=owner.flats.all()).order_by('-convenient_time')


def get_receipt_services() -> Iterable[ReceiptService]:
    return ReceiptService.objects.all()


def get_flats_with_indebtedness() -> Iterable[Flat]:
    return [flat for flat in get_flats() if flat.balance < 0]


def get_flats_without_indebtedness() -> Iterable[Flat]:
    return [flat for flat in get_flats() if flat.balance >= 0]


def get_indebtedness() -> float:
    indebtedness = Receipt.objects.filter(status__in=['1', '2']).aggregate(Sum('summary'))['summary__sum']
    return 0.0 if indebtedness is None else indebtedness

def get_flat_balances() -> float:
    return sum([flat.balance for flat in get_flats_without_indebtedness()])


def create_cashbox_out(**kwargs) -> CashboxRecord:
    return CashboxRecord.objects.create(**kwargs)


def get_tickets_in_progress() -> Iterable[Ticket]:
    return Ticket.objects.filter(status='2')


def get_new_tickets() -> Iterable[Ticket]:
    return Ticket.objects.filter(status='1')


def get_cashbox_in_per_year(year: int) -> list[float]:
    result = []
    for month in range(1, 13):
        month_in = CashboxRecord.objects.filter(
            payment_type__type="0", 
            date__year=year, 
            date__month=month).aggregate(Sum('summary'))['summary__sum']
        result.append(0.0 if month_in is None else float(month_in))
    return result


def get_cashbox_out_per_year(year: int) -> list[float]:
    result = []
    for month in range(1, 13):
        month_out = CashboxRecord.objects.filter(
            payment_type__type="1", 
            date__year=year, 
            date__month=month).aggregate(Sum('summary'))['summary__sum']
        result.append(0.0 if month_out is None else float(month_out))
    return result


def get_indebtedness_per_year(year: int) -> list[float]:
    result = []
    for month in range(1, 13):
        month_indebtedness = Receipt.objects.filter(
            creation_date__year=year,
            creation_date__month=month,
            status__in=['1', '2']).aggregate(Sum('summary'))['summary__sum']
        result.append(0.0 if month_indebtedness is None else float(month_indebtedness))
    return result


def get_repaid_indebtedness_per_year(year: int) -> list[float]:
    result = []
    for month in range(1, 13):
        month_repaid_indebtedness = Receipt.objects.filter(
            creation_date__year=year,
            creation_date__month=month,
            status='3').aggregate(Sum('summary'))['summary__sum']
        result.append(0.0 if month_repaid_indebtedness is None else float(month_repaid_indebtedness))
    return result
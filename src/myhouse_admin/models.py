import logging
import os

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core import validators
from django.db import models
from django.db.models.aggregates import Avg, Sum
from django.db.models.fields.files import ImageField
from django.dispatch import receiver

from users.models import User, Employee, Owner, Role, get_upload_path


logger = logging.getLogger(__name__)


class House(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    image1 = models.ImageField(upload_to=get_upload_path)
    image2 = models.ImageField(upload_to=get_upload_path)
    image3 = models.ImageField(upload_to=get_upload_path)
    image4 = models.ImageField(upload_to=get_upload_path)
    image5 = models.ImageField(upload_to=get_upload_path)
    workers = models.ManyToManyField(Employee)

    def __str__(self) -> str:
        return self.name

    class Meta:
        unique_together = ('name', 'address')
        ordering = ('name',)

    @property
    def floor_count(self):
        result = 0
        result += sum(section.floor_set.count() for section in self.section_set.all())
        return result

    @property
    def owners(self):
        return set([flat.owner for flat in Flat.objects.filter(floor__section__house=self)])


class Unit(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.name

    @property
    def in_tariff(self) -> float:
        return True if ReceiptService.objects.filter(service__unit=self).count() > 0 else False


class Service(models.Model):
    name = models.CharField(max_length=255)
    in_meter = models.BooleanField(default=False)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='services')

    def __str__(self) -> str:
        return self.name

    @property
    def in_tariff(self) -> float:
        return True if ReceiptService.objects.filter(service=self).count() > 0 else False
    
    class Meta:
        unique_together = ('name', )


class Tariff(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    edit_date = models.DateTimeField(auto_now=True)
    services = models.ManyToManyField(Service, through='TariffService')

    def __str__(self) -> str:
        return self.name


class TariffService(models.Model):
    tariff = models.ForeignKey(Tariff, on_delete=models.CASCADE, related_name="tariff_services")
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    price = models.FloatField(validators=[validators.MinValueValidator(0.0)])


class Section(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    house = models.ForeignKey(House, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ('name', 'house')

    def __str__(self) -> str:
        return self.name
    
    @property
    def owners(self):
        return set([flat.owner for flat in Flat.objects.filter(floor__section=self)])


class Floor(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ('name', 'section')

    def __str__(self) -> str:
        return self.name

    @property
    def owners(self):
        return set([flat.owner for flat in Flat.objects.filter(floor=self)])


class Flat(models.Model):
    number = models.PositiveIntegerField()
    square = models.FloatField(validators=[validators.MinValueValidator(0.0)])
    floor = models.ForeignKey(Floor, on_delete=models.SET_NULL, null=True)
    owner = models.ForeignKey(Owner, on_delete=models.SET_NULL, null=True, related_name='flats')
    tariff = models.ForeignKey(Tariff, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ('number', 'floor')

    @property
    def flat_personal_account(self):
        try:
            return self.personal_account
        except:
            return None

    @property
    def to_string(self) -> str:
        return f'№{self.number}, {self.floor.section.house.name}'

    def __str__(self) -> str:
        return f'{self.number}'

    @property
    def balance(self) -> float:
        flat_cb_in: float = CashboxRecord.objects.filter(personal_account__flat=self).aggregate(Sum('summary'))['summary__sum']
        flat_receipts_summary: float = Receipt.objects.filter(flat=self, status='3').aggregate(Sum('summary'))['summary__sum']
        flat_cb_in = 0.0 if flat_cb_in is None else flat_cb_in
        flat_receipts_summary = 0.0 if flat_receipts_summary is None else flat_receipts_summary
        return flat_cb_in - flat_receipts_summary

    @property
    def actual_balance(self) -> float:
        flat_cb_in: float = CashboxRecord.objects.filter(personal_account__flat=self).aggregate(Sum('summary'))['summary__sum']
        flat_receipts_summary: float = Receipt.objects.filter(flat=self).aggregate(Sum('summary'))['summary__sum']
        flat_cb_in = 0.0 if flat_cb_in is None else flat_cb_in
        flat_receipts_summary = 0.0 if flat_receipts_summary is None else flat_receipts_summary
        return flat_cb_in - flat_receipts_summary

    @property
    def indebtedness(self) -> float:
        flat_receipts_summary: float = Receipt.objects.filter(flat=self, status__in=['1', '2']).aggregate(Sum('summary'))['summary__sum']
        return 0.0 if flat_receipts_summary is None else flat_receipts_summary

    @property
    def avg_spending(self) -> float:
        try:
            return float(self.receipts.all().aggregate(Avg('summary'))['summary__avg'])
        except:
            return 0.00


class PersonalAccount(models.Model):
    STATUSES = (
        ('0', 'Не активен'),
        ('1', 'Активен'),
    )
    uid = models.CharField(max_length=50, unique=True)
    flat = models.OneToOneField(Flat, on_delete=models.SET_NULL, null=True, related_name='personal_account')
    status = models.CharField(max_length=1, choices=STATUSES)

    def __str__(self):
        return self.uid

    @classmethod
    def export_to_excel(cls) -> dict:
        data = [['Лицевой счет', 'Статус', 'Дом', 'Секция', 'Квартира', 'Владелец', 'Остаток']]
        for a in cls.objects.filter().all():
            data.append([str(a.uid), str(a.get_status_display()), 
                str(a.flat.floor.section.house),
                str(a.flat.floor.section), str(a.flat),
                str(a.flat.owner),
                f'{a.flat.actual_balance:.2f}' if a.flat else "0.0"
            ])
        return data



class PaymentType(models.Model):
    TYPES = (
        ('0', 'Приход'),
        ('1', 'Расход'),
    )
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=1, choices=TYPES)

    class Meta:
        unique_together = ('name', 'type')

    def __str__(self) -> str:
        return self.name


class MeterReading(models.Model):
    STATUSES = (
        ('1', 'Новое'),
        ('2', 'Учтено'),
        ('3', 'Учтено и оплачено'),
        ('4', 'Нулевое'),
    )
    number = models.CharField('Номер', max_length=50, unique=True)
    flat = models.ForeignKey(Flat, on_delete=models.CASCADE)
    reading_date = models.DateField()
    status = models.CharField(max_length=1, choices=STATUSES)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    testimony = models.FloatField(validators=[validators.MinValueValidator(0.0)])


class Receipt(models.Model):
    STATUSES = (
        ('1', 'Не оплачена'),
        ('2', 'Частично оплачена'),
        ('3', 'Оплачена'),
    )
    number = models.CharField('Номер', max_length=50, unique=True)
    is_made = models.BooleanField(default=False)
    status = models.CharField(max_length=1, choices=STATUSES, default='1')
    creation_date = models.DateField()
    start_date = models.DateField()
    end_date = models.DateField()
    flat = models.ForeignKey(Flat, on_delete=models.CASCADE, related_name='receipts')
    summary = models.FloatField(validators=[validators.MinValueValidator(0.0)])


class ReceiptService(models.Model):
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, related_name='r_services')
    service = models.ForeignKey(Service, on_delete=models.DO_NOTHING)
    consumption = models.FloatField(validators=[validators.MinValueValidator(0.0)])
    unit = models.ForeignKey(Unit, on_delete=models.DO_NOTHING)
    unit_price = models.FloatField(validators=[validators.MinValueValidator(0.0)])
    total_price = models.FloatField(validators=[validators.MinValueValidator(0.0)])


class CashboxRecord(models.Model):
    number = models.CharField(max_length=50, unique=True)
    date = models.DateField('Дата')
    is_made = models.BooleanField(default=False)
    payment_type = models.ForeignKey(PaymentType, on_delete=models.CASCADE)
    personal_account = models.ForeignKey(PersonalAccount, on_delete=models.CASCADE, null=True, blank=True)
    manager = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    summary = models.FloatField(validators=[validators.MinValueValidator(0.0)])
    comment = models.TextField(null=True, blank=True)
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ('-date', )

    @classmethod
    def export_to_excel(cls) -> dict:
        data = [['#', 'Дата', 'Приход/расход', 'Статус', 'Статья', 
            'Квитанция', 'Услуга', 'Сумма', 'Валюта', 
            'Владелец квартиры', 'Лицевой счет']]
        for cbr in cls.objects.filter().all():
            data.append([str(cbr.number), str(cbr.date), 
                str(cbr.payment_type.get_type_display()),
                "Проведен" if cbr.is_made else "Не проведен",
                str(cbr.payment_type.name), 
                f"{cbr.receipt.number} от {cbr.receipt.creation_date}" if cbr.receipt else '', 
                '', f'{int(cbr.summary)}', 'UAH',
                str(cbr.personal_account.flat.owner) if cbr.personal_account else '',
                cbr.personal_account.uid if cbr.personal_account else ''
            ])
        return data

    def export_to_excel(self) -> dict:
        data = []
        data.append(['Платеж', self.number])
        data.append(['Дата', str(self.date)])
        data.append(['Владелец квартиры', str(self.personal_account.flat.owner) if self.personal_account else ''])
        data.append(['Лицевой счет', self.personal_account.uid if self.personal_account else ''])
        data.append(['Приход/расход', str(self.payment_type.get_type_display())])
        data.append(['Статус', "Проведен" if self.is_made else "Не проведен"])
        data.append(['Статья', str(self.payment_type.name)])
        data.append(['Квитанция', f"{self.receipt.number} от {self.receipt.creation_date}" if self.receipt else ''])
        data.append(['Услуга', ''])
        data.append(['Сумма', f'{int(self.summary)}'])
        data.append(['Валюта', 'UAH'])
        data.append(['Комментарий', self.comment])
        data.append(['Менеджер', str(self.manager) if self.manager else ''])
        return data


class Ticket(models.Model):
    STATUSES = (
        ('1', 'Новое'),
        ('2', 'В работе'),
        ('3', 'Выполнено'),
    )
    convenient_time = models.DateTimeField('Удобное время')
    added_time = models.DateTimeField(auto_now_add=True)
    master_type = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    status = models.CharField(max_length=1, choices=STATUSES, default='1')
    master = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    flat = models.ForeignKey(Flat, on_delete=models.CASCADE)
    comment = models.TextField(null=True, blank=True)

class Message(models.Model):
    sender = models.ForeignKey(Employee, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    send_date = models.DateTimeField(auto_now_add=True)
    for_debtors = models.BooleanField(default=False)
    recipients = models.ManyToManyField(Owner, related_name='messages')
    house = models.ForeignKey(House, on_delete=models.CASCADE, null=True, blank=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, null=True, blank=True)
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, null=True, blank=True)
    flat = models.ForeignKey(Flat, on_delete=models.CASCADE, null=True, blank=True)

    @property
    def recipients_to_str(self) -> str:
        if self.flat is not None:
            return f"{self.flat.floor.section.house}, {self.flat.floor.section}, {self.flat.floor}, кв.{self.flat}"
        elif self.floor is not None:
            return f"{self.floor.section.house}, {self.floor.section}, {self.floor}"
        elif self.section is not None:
            return f"{self.section.house}, {self.section}"
        elif self.house is not None:
            return f"{self.house}"
        else:
            return "Всем"


class Block(models.Model):
    poster = models.ImageField(upload_to=get_upload_path, null=True, blank=True)
    heading = models.CharField(max_length=255)
    description = models.TextField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


class TariffImage(models.Model):
    image = models.ImageField(upload_to=get_upload_path, null=True, blank=True)
    signature = models.CharField(max_length=100)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.__class__.objects.exclude(id=self.id).delete()
        super(SingletonModel, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        try:
            return cls.objects.get()
        except cls.DoesNotExist:
            return cls()


class PaymentDetails(SingletonModel):
    company_name = models.CharField(max_length=255)
    details = models.TextField()


class MainPage(SingletonModel):
    slide1 = models.ImageField(upload_to=get_upload_path)
    slide2 = models.ImageField(upload_to=get_upload_path)
    slide3 = models.ImageField(upload_to=get_upload_path)
    heading = models.CharField(max_length=100)
    short_text = models.TextField()
    show_links_on_apps = models.BooleanField(default=False)
    blocks = GenericRelation(Block, related_query_name='block')
    seo_title = models.CharField(max_length=255, null=True, blank=True)
    seo_description = models.TextField(null=True, blank=True)
    seo_keywords = models.TextField(null=True, blank=True)

    @property
    def get_all_generic_relation(self):
        return self.blocks.all()


class AboutUsPage(SingletonModel):
    heading = models.CharField(max_length=100)
    short_text = models.TextField()
    director_photo = models.ImageField(upload_to=get_upload_path)
    ai_heading =models.CharField(max_length=100)
    ai_short_text = models.TextField()
    seo_title = models.CharField(max_length=255, null=True, blank=True)
    seo_description = models.TextField(null=True, blank=True)
    seo_keywords = models.TextField(null=True, blank=True)


class Document(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(
        upload_to=get_upload_path, 
        validators=[validators.FileExtensionValidator(
            allowed_extensions=('pdf', 'jpg'))],
        error_messages={
            'invalid_extension': 'Этот формат не поддерживается'})
    about_us_page = models.ForeignKey(AboutUsPage, on_delete=models.CASCADE)


class AboutUsPageImage(models.Model):
    about_us_page = models.ForeignKey(AboutUsPage, on_delete=models.CASCADE, related_name='images')
    image = ImageField(upload_to=get_upload_path)

    @property
    def foreign_key(self):
        return self.about_us_page

    @foreign_key.setter
    def foreign_key(self, value):
        self.about_us_page = value


class AboutUsPageAdditionalImage(models.Model):
    about_us_page = models.ForeignKey(AboutUsPage, on_delete=models.CASCADE, related_name='additional_images')
    image = ImageField(upload_to=get_upload_path)

    @property
    def foreign_key(self):
        return self.about_us_page

    @foreign_key.setter
    def foreign_key(self, value):
        self.about_us_page = value


class ServicesPage(SingletonModel):
    services = GenericRelation(Block, related_query_name='service')
    seo_title = models.CharField(max_length=255, null=True, blank=True)
    seo_description = models.TextField(null=True, blank=True)
    seo_keywords = models.TextField(null=True, blank=True)
    
    @property
    def get_all_generic_relation(self):
        return self.services.all()


class TariffPage(SingletonModel):
    heading = models.CharField(max_length=100)
    short_text = models.TextField()
    seo_title = models.CharField(max_length=255, null=True, blank=True)
    seo_description = models.TextField(null=True, blank=True)
    seo_keywords = models.TextField(null=True, blank=True)
    blocks = GenericRelation(TariffImage, related_query_name='block')

    @property
    def get_all_generic_relation(self):
        return self.blocks.all()


class ContactsPage(SingletonModel):
    heading = models.CharField(max_length=100)
    short_text = models.TextField()
    commercial_site_link = models.URLField()
    fio = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone_number = models.CharField("Номер телефона", max_length=20, unique=True,
        validators=[
            validators.RegexValidator(
                regex=r'^(?:\+38)?(?:\(0[0-9][0-9]\)[ .-]?[0-9]{3}[ .-]?[0-9]{2}[ .-]?[0-9]{2}|044[ .-]?[0-9]{3}[ .-]?[0-9]{2}[ .-]?[0-9]{2}|0[0-9][0-9][0-9]{7})$')
        ])
    email = models.EmailField('E-mail')
    map = models.TextField()
    seo_title = models.CharField(max_length=255, null=True, blank=True)
    seo_description = models.TextField(null=True, blank=True)
    seo_keywords = models.TextField(null=True, blank=True)

    @property
    def phone_link(self):
        return 'tel:' + str(self.phone_number).replace(' ', '').replace('(', '').replace(')', '').replace('-', '')
    
    @property
    def mail_to(self):
        return f'mailto:{self.email}'


image_attributes = (
    'image', 'image1', 'image2', 'image3', 'image4', 'image5', 
    'avatar', 'poster', 'file', 'slide1', 'slide2', 'slide3',
    'director_photo')


@receiver(models.signals.post_delete, sender=Owner)
@receiver(models.signals.post_delete, sender=House)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding sender object is deleted.
    """
    for attribute in image_attributes:
        if hasattr(instance, attribute):
            attr = getattr(instance, attribute)
            if attr:
                try:
                    if os.path.isfile(attr.path):
                        os.remove(attr.path)
                except ValueError:
                    pass

@receiver(models.signals.post_delete, sender=Owner)
@receiver(models.signals.post_delete, sender=House)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding sender object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        sender_obj = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return False
    old_file = new_file = None
    for attribute in image_attributes:
        if hasattr(sender_obj, attribute):
            old_file = getattr(sender_obj, attribute)
        if hasattr(instance, attribute):
            new_file = getattr(instance, attribute)

    if not old_file == new_file:
        try:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)
        except ValueError as e:
            pass
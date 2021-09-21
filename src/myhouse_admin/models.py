import os

from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core import validators
from django.db import models
from django.db.models.fields.files import ImageField
from django.dispatch import receiver

from users.models import User, Employee, Owner, Role, get_upload_path


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


class Unit(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=255)
    in_meter = models.BooleanField(default=False)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='services')

    def __str__(self) -> str:
        return self.name
    
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


class Floor(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ('name', 'section')

    def __str__(self) -> str:
        return self.name


class Flat(models.Model):
    number = models.PositiveIntegerField()
    square = models.FloatField(validators=[validators.MinValueValidator(0.0)])
    floor = models.ForeignKey(Floor, on_delete=models.SET_NULL, null=True)
    owner = models.ForeignKey(Owner, on_delete=models.SET_NULL, null=True, related_name='flats')
    tariff = models.ForeignKey(Tariff, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ('number', 'floor')

    def clean(self):
        """
        Validate number and floor__section are unique together
        """
        if self.number and self.floor.section:
            if self.__class__.objects.filter(
                number=self.number, 
                floor=self.floor, 
                floor__section=self.floor.section).exists():
                raise ValidationError(
                    'Этот номер квартиры уже присутствует в секции',
                    code='unique_together',
                )

    @property
    def flat_personal_account(self):
        try:
            return self.personal_account
        except:
            return None

    @property
    def to_string(self) -> str:
        return f'Квартира №{self.number}, {self.floor.section.house.name}'

    def __str__(self) -> str:
        return f'{self.number}'


class PersonalAccount(models.Model):
    STATUSES = (
        ('0', 'Не активен'),
        ('1', 'Активен'),
    )
    uid = models.CharField(max_length=50, unique=True)
    flat = models.OneToOneField(Flat, on_delete=models.SET_NULL, null=True, related_name='personal_account')
    status = models.CharField(max_length=1, choices=STATUSES)
    summary = models.FloatField(default=0.0)

    def __str__(self):
        return self.uid


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


class CashboxRecord(models.Model):
    number = models.CharField(max_length=50, unique=True)
    date = models.DateField('Дата')
    is_made = models.BooleanField(default=False)
    payment_type = models.ForeignKey(PaymentType, on_delete=models.CASCADE)
    personal_account = models.ForeignKey(PersonalAccount, on_delete=models.CASCADE, null=True, blank=True)
    manager = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    summary = models.FloatField(validators=[validators.MinValueValidator(0.0)])
    comment = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ('-date', )


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
    flat = models.ForeignKey(Flat, on_delete=models.CASCADE)
    summary = models.FloatField(validators=[validators.MinValueValidator(0.0)])


class ReceiptService(models.Model):
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.DO_NOTHING)
    consumption = models.FloatField(validators=[validators.MinValueValidator(0.0)])
    unit = models.ForeignKey(Unit, on_delete=models.DO_NOTHING)
    unit_price = models.FloatField(validators=[validators.MinValueValidator(0.0)])
    total_price = models.FloatField(validators=[validators.MinValueValidator(0.0)])


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
    text = models.TextField()
    send_date = models.DateTimeField(auto_now_add=True)
    recipients = models.CharField(max_length=100)


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
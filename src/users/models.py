from datetime import datetime as dt
from pathlib import Path
from typing import Iterable

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core import validators
from multiselectfield import MultiSelectField

from users.managers import UserManager


def get_upload_path(instance, filename):
    return Path('uploads') / dt.now().strftime('%Y/%m-%d') / filename


class User(AbstractUser):
    USER_STATUSES = (
        ('0', 'Отключен'),
        ('1', 'Новый'),
        ('2', 'Активен'),
    )
    username = None
    email = models.EmailField('E-mail', unique=True)
    phone_number = models.CharField("Номер телефона", max_length=20, unique=True,
        # valid=[+38(093)1350239,+38(093)135-02-39,+38(093)135 02 39,+380931350239,0931350239,+380445371428, +38(044)5371428,+38(044)537 14 28,+38(044)537-14-28,+38(044) 537.14.28,044.537.14.28,0445371428,044-537-1428,(044)537-1428,044 537-1428]
        # invalid = [+83(044)537 14 28,088 537-1428]
        validators=[
            validators.RegexValidator(
                regex=r'^(?:\+38)?(?:\(0[0-9][0-9]\)[ .-]?[0-9]{3}[ .-]?[0-9]{2}[ .-]?[0-9]{2}|044[ .-]?[0-9]{3}[ .-]?[0-9]{2}[ .-]?[0-9]{2}|0[0-9][0-9][0-9]{7})$')
        ])
    status = models.CharField(max_length=1, choices=USER_STATUSES, default='1')

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number']

    def __str__(self) -> str:
        return self.email

    def save(self, *args, **kwargs):
        if self.status == '0':
            self.is_active = False
        else:
            self.is_active = True
        super().save(*args, **kwargs)

    @property
    def user_owner(self):
        try:
            return self.owner
        except:
            return None


class Role(models.Model):
    ABILITIES = (
        ('1', 'Статистика'),
        ('2', 'Касса'),
        ('3', 'Квитанции на оплату'),
        ('4', 'Лицевые счета'),
        ('5', 'Квартиры'),
        ('6', 'Владельцы квартир'),
        ('7', 'Дома'),
        ('8', 'Сообщения'),
        ('9', 'Заявки вызова мастера'),
        ('10', 'Счетчики'),
        ('11', 'Управление сайтом'),
        ('12', 'Услуги'),
        ('13', 'Тарифы'),
        ('14', 'Роли'),
        ('15', 'Пользователи'),
        ('16', 'Платежные реквизиты'),
    )
    name = models.CharField(max_length=50)
    abilities = MultiSelectField(choices=ABILITIES)

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ('id',)


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    
    def save(self, *args, **kwargs):
        self.user.is_staff = True
        super().save(*args, **kwargs)

    class Meta:
        ordering = ('id',)

    def __str__(self) -> str:
        return f'{self.role} - {self.user.get_full_name()}'


class Owner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birth_date = models.DateField("Дата рождения", null=True, blank=True)
    avatar = models.ImageField(upload_to=get_upload_path, null=True, blank=True)
    ID = models.CharField('ID пользователя', max_length=50, unique=True)
    about = models.TextField(null=True, blank=True)
    viber = models.CharField(max_length=20, null=True, blank=True)
    telegram = models.CharField(max_length=50, null=True, blank=True)

    @property
    def houses_to_str(self) -> str:
        return ',</br>'.join({flat.floor.section.house.name for flat in self.flats.all()})

    @property
    def houses(self) -> set:
        return {flat.floor.section.house for flat in self.flats.all()}

    @property
    def flats_to_str(self) -> str:
        return ',</br>'.join({str(flat.to_string) for flat in self.flats.all()})

    @property
    def first_name(self) -> str:
        try:
            return self.user.first_name.split(' ')[0]
        except:
            return self.user.first_name

    @property
    def second_name(self) -> str:
        try:
            return self.user.first_name.split(' ')[1]
        except:
            return ''

    @property
    def have_debts(self) -> bool:
        for flat in self.flats.all():
            if flat.actual_balance < 0:
                return True
        return False

    @property
    def messages(self):
        return 
    
    def __str__(self) -> str:
        return f'{self.user.last_name} {self.user.first_name}'

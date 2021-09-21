from django.contrib import admin
from django.contrib.admin.decorators import register

from .models import User, Role, Owner, Employee

admin.site.register(User)
admin.site.register(Role)
admin.site.register(Owner)
# admin.site.register(Employee)


@register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Employee._meta.fields]
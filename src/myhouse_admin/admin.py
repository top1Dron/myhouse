from django.contrib import admin
from .models import Receipt, ReceiptService, ServicesPage, Block, Document, AboutUsPage, House, Section, Floor, Unit, Service
# Register your models here.

admin.site.register(ServicesPage)
admin.site.register(Block)
admin.site.register(Document)
admin.site.register(AboutUsPage)
admin.site.register(House)
admin.site.register(Section)
admin.site.register(Floor)
admin.site.register(Unit)
admin.site.register(Service)
admin.site.register(ReceiptService)
admin.site.register(Receipt)

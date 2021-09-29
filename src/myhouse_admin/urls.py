from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path, reverse_lazy

from myhouse_admin.views import (message_views, personal_account_views, statistic_views, 
    settings, users, site_management, house_views, flat_views, cashbox_views,
    meters_views, receipt_views, master_calling_views)


app_name = 'myhouse_admin'

urlpatterns = [

    # authorization block
    path('site/login/', users.employee_views.admin_login, name="admin_login"),
    path('site/welcome-page/', users.employee_views.welcome, name="welcome"),
    path('site/logout/', users.employee_views.admin_logout, name="logout"),

    # houses block
    path('house/index/', staff_member_required(house_views.HouseListView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name="house_list"),
    path('house/create/', staff_member_required(house_views.HouseCreateView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name="house_create"),
    path('house/update/<int:pk>/', staff_member_required(house_views.HouseUpdateView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name="house_update"),
    path('house/delete-employee/<int:employee_pk>/<int:house_pk>/', house_views.delete_employee_from_house, name="delete_house_employee"),
    path('house/<int:pk>/delete/', house_views.delete_house, name="house_delete"),
    path('house/<int:pk>/', staff_member_required(house_views.HouseDetailView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name="house_detail"),

    # flats block
    path('flat/index/', staff_member_required(flat_views.FlatListView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name="flat_list"),
    path('flat/create/', staff_member_required(flat_views.FlatCreateView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name='flat_create'),
    path('flat/load-house-sections/', flat_views.load_house_sections, name="load_house_sections"),
    path('flat/load-house-flats/', flat_views.load_house_flats, name="load_house_flats"),
    path('flat/load-section-floors/', flat_views.load_section_floors, name="load_section_floors"),
    path('flat/load-section-flats/', flat_views.load_section_flats, name="load_section_flats"),
    path('flat/load-empty-flats/', flat_views.load_empty_flats, name="load_empty_flats"),
    path('flat/load-floor-flats/', flat_views.load_floor_flats, name="load_floor_flats"),
    path('flat/load-section-flats-without-pa/', flat_views.load_section_flats_without_pa, name="load_section_flats_without_pa"),
    path('flat/load-flat-details/', flat_views.load_flat_details, name="load_flat_details"),
    path('flat/load-flat-meters/', flat_views.load_flat_meters, name="load_flat_meters"),
    path('flat/load-owner-flats/', flat_views.load_owner_flats, name="load_owner_flats"),
    path('flat/load-section-flats-on-update/', flat_views.load_section_flats_on_update, name="load_section_flats_on_update"),
    path('flat/load-section-flats-without-pa-on-update/', flat_views.load_section_flats_on_update_pa, name="load_section_flats_on_update_pa"),
    path('flat/update/<int:pk>/', staff_member_required(flat_views.FlatUpdateView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name='flat_update'),
    path('flat/delete/<int:pk>/', flat_views.delete_flat, name="flat_delete"),
    path('flat/<int:pk>/', staff_member_required(flat_views.FlatDetailView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name="flat_detail"),

    # personal_accounts block
    path('account/index/', staff_member_required(personal_account_views.PersonalAccountListView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name="personal_account_list"),
    path('account/create/', staff_member_required(personal_account_views.PersonalAccountCreateView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name='personal_account_create'),
    path('account/export/', personal_account_views.export_to_excel, name="personal_account_export_to_excel"),
    path('account/delete/<int:pk>/', personal_account_views.delete_personal_account, name="personal_account_delete"),
    path('account/update/<int:pk>/', staff_member_required(personal_account_views.PersonalAccountUpdateView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name='personal_account_update'),
    path('account/<int:pk>/', staff_member_required(personal_account_views.PersonalAccountDetailView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name='personal_account_detail'),

    # cashbox block
    path('account-transaction/index/', staff_member_required(cashbox_views.CashboxListView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name="cashbox_list"),
    path('account-transaction/create/', staff_member_required(cashbox_views.CashboxRecordCreateView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name="cashbox_record_create"),
    path('account-transaction/export/', cashbox_views.export_to_excel, name="cashbox_record_export_to_excel"),
    path('account-transaction/load-owner-accounts/', cashbox_views.load_owner_accounts, name="load_owner_accounts"),
    path('account-transaction/delete/<int:pk>/', cashbox_views.delete_cashbox_record, name="cbr_delete"),
    path('account-transaction/export-one/<int:pk>/', cashbox_views.export_one_to_excel, name="cbr_export_one"),
    path('account-transaction/update/<int:pk>/', staff_member_required(cashbox_views.CashboxRecordUpdateView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name="cashbox_record_update"),
    path('account-transaction/<int:pk>/', staff_member_required(cashbox_views.CashboxRecordDetailView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name="cashbox_record_detail"),

    # receipt block
    path('invoice/index/', staff_member_required(receipt_views.ReceiptListView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name="receipt_list"),
    path('invoice/create/', receipt_views.receipt_create_view, name="receipt_create"),
    path('invoice/ajax-delete-many/', receipt_views.receipt_delete_many, name="receipt_delete_many"),
    path('invoice/print/<int:pk>/', receipt_views.export_receipt_to_excel, name="receipt_export"),
    path('invoice/update/<int:pk>/', receipt_views.receipt_update_view, name="receipt_update"),
    path('invoice/delete/<int:pk>/', receipt_views.delete_receipt_view, name="receipt_delete"),
    path('invoice/<int:pk>/', staff_member_required(receipt_views.ReceiptDetailView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name="receipt_detail"),

    # message block
    path('message/index/', staff_member_required(message_views.MessageListView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name="message_list"),
    path('message/create/', staff_member_required(message_views.MessageCreateView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name="message_create"),
    path('message/ajax-delete-many/', message_views.message_delete_many, name="message_delete_many"),
    path('message/delete/<int:pk>/',  message_views.delete_message, name="message_delete"),
    path('message/<int:pk>/', staff_member_required(message_views.MessageDetailView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name="message_detail"),

    # master request block
    path('master-request/index', staff_member_required(master_calling_views.TicketListView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name="master_request_list"),
    path('master-request/create', staff_member_required(master_calling_views.TicketCreateView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name="master_request_create"),
    path('master-request/update/<int:pk>/', staff_member_required(master_calling_views.TicketUpdateView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name="master_request_update"),
    path('master-request/delete/<int:pk>/', master_calling_views.delete_ticket, name="master_request_delete"),
    path('master-request/<int:pk>/', staff_member_required(master_calling_views.TicketDetailView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name="master_request_detail"),

    # meter block
    path('counter-data/counters/', staff_member_required(meters_views.MeterListView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name="meter_list"),
    path('counter-data/counter-list/', staff_member_required(meters_views.MeterReadingListView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name="meter_reading_list"),
    path('counter-data/create/', staff_member_required(meters_views.MeterReadingCreateView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name="meter_create"),
    path('counter-data/delete/<int:pk>/', meters_views.delete_meter_reading, name="meter_reading_delete"),
    path('counter-data/update<int:pk>/', staff_member_required(meters_views.MeterReadingUpdateView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name="meter_reading_update"),
    path('counter-data/<int:pk>/', staff_member_required(meters_views.MeterReadingDetailView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name="meter_reading_detail"),
    
    # site management block
    path('website/home/', site_management.views.main_page, name="main_page"),
    path('website/about/', site_management.views.about_us_page, name="about_us_page"),
    path('website/services/', site_management.views.services_page, name="services_page"),
    path('website/tariffs/', site_management.views.tariff_page, name="tariff_page"),
    path('website/contact/', site_management.views.contacts_page, name="contacts_page"),
    path('website/delete-about-image/<int:pk>/', site_management.views.delete_about_image, name="delete_about_image"),
    path('website/delete-about-additional-image/<int:pk>/', site_management.views.delete_about_ad_image, name="delete_about_ad_image"),
    path('website/delete-services/<int:pk>/', site_management.views.delete_block, name="delete_block"),

    # settings block
    path('user-admin/role/', settings.roles_views.roles, name="roles"),
    path('pay-company/index/', settings.roles_views.payment_details, name="payment_details"),
    path('service/index/', settings.service_unit_views.service_unit_view, name='service_unit'),
    path('service/delete-unit/<int:pk>/', settings.service_unit_views.unit_delete, name="unit_delete"),
    path('service/delete-service/<int:pk>/', settings.service_unit_views.service_delete, name="service_delete"),
    path('tariff/index/', staff_member_required(settings.tariff_views.TariffListView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name="tariff_list"),
    path('tariff/create/', staff_member_required(settings.tariff_views.TariffCreateView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name="tariff_create"),
    path('tariff/update/<int:pk>/', staff_member_required(settings.tariff_views.TariffUpdateView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name="tariff_update"),
    path('tariff/get-service-unit/', settings.tariff_views.get_service_unit, name='get_service_unit'),
    path('tariff/get-tariff-service-price/', settings.tariff_views.get_tariff_service_price, name='get_tariff_service_price'),
    path('tariff/<int:pk>/delete_service/<int:tariff_service_pk>/', settings.tariff_views.delete_tariff_service, name='tariff_service_delete'),
    path('tariff/<int:pk>/delete/', settings.tariff_views.delete_tariff, name="tariff_delete"),
    path('tariff/<int:pk>/', staff_member_required(settings.tariff_views.TariffDetailView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name="tariff_detail"),
    path('transaction-purpose/index/', staff_member_required(settings.payment_type_views.PaymentTypeListView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name="payment_type_list"),
    path('transaction-purpose/create/', staff_member_required(settings.payment_type_views.PaymentTypeCreateView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name="payment_type_create"),
    path('transaction-purpose/update/<int:pk>/', staff_member_required(settings.payment_type_views.PaymentTypeUpdateView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name="payment_type_update"),
    path('transaction-purpose/<int:pk>/delete/', settings.payment_type_views.delete_payment_type, name="payment_type_delete"),

    # workers block
    path('user-admin/index/', staff_member_required(users.employee_views.EmployeeListView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name="worker_list"),
    path('user-admin/create/', staff_member_required(users.employee_views.EmployeeCreateView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name="worker_create"),
    path('user-admin/update/<int:pk>/', staff_member_required(users.employee_views.EmployeeUpdateView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name="worker_update"),
    path('user-admin/delete/<int:pk>/', users.employee_views.delete_employee, name="employee_delete"),
    path('user-admin/get-employee-role/<int:pk>/', users.employee_views.get_employee_role, name="employee_role"),
    path('user-admin/<int:pk>/', staff_member_required(users.employee_views.EmployeeDetailView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name="worker_detail"),

    # owners block
    path('user/index/', staff_member_required(users.owner_views.OwnerListView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name="owner_list"),
    path('user/create/', staff_member_required(users.owner_views.OwnerCreateView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name="owner_create"),
    path('user/update/<int:pk>/', staff_member_required(users.owner_views.OwnerUpdateView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name="owner_update"),
    path('user/<int:pk>/delete/', users.owner_views.delete_owner, name='owner_delete'),
    path('user/<int:pk>/', staff_member_required(users.owner_views.OwnerDetailView.as_view(), login_url=reverse_lazy('myhouse_admin:admin_login')), name='owner_detail'),

    # statistics block
    path('', statistic_views.index, name='index'),
]

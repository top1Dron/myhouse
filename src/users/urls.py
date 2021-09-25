from django.urls import path

from users.views import cabinet_views, message_views, receipt_views, summary_views, tariff_views, master_request_views

app_name = 'users'

urlpatterns = [
    path('site/login/', cabinet_views.cabinet_login, name="login"),
    path('site/logout/', cabinet_views.cabinet_logout, name="logout"),
    
    path('user/view/', cabinet_views.CabinetDetailView.as_view(), name="profile"),
    path('user/update/', cabinet_views.CabinetUpdateView.as_view(), name="profile_update"),

    path('invoice/index/', receipt_views.ReceiptListView.as_view(), name="receipt_index"),
    path('invoice/pay/<int:pk>/', receipt_views.pay_for_receipt, name="receipt_pay"),
    path('invoice/<int:pk>/', receipt_views.ReceiptDetailView.as_view(), name="receipt_detail"),

    path('tariff/index/', tariff_views.FlatTariffDetailView.as_view(), name="tariff_index"),

    path('message/index/', message_views.CabinetMessageListView.as_view(), name="message_index"),
    path('message/ajax-delete-many/', message_views.delete_messages, name="message_delete_many"),
    path('message/delete/<int:pk>/', message_views.delete_message, name="message_delete"),
    path('message/<int:pk>/', message_views.CabinetMessageDetailView.as_view(), name="message_detail"),

    path('master-request/index/', master_request_views.OwnerRequestsDetailView.as_view(), name="owner_requests_list"),
    path('master-request/create/', master_request_views.OwnerRequestCreateView.as_view(), name="owner_requests_create"),
    path('master-request/delete/<int:pk>/', master_request_views.delete_ticket, name="master_request_delete"),

    path('open/', cabinet_views.open_owner_cabinet, name="open_cabinet"),
    path('', summary_views.summary, name="summary"),
]

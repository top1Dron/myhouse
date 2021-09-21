from django.urls import path

from users.views import cabinet_views, summary_views, tariff_views, master_request_views

app_name = 'users'

urlpatterns = [
    path('site/login/', cabinet_views.cabinet_login, name="login"),
    
    path('user/view/', cabinet_views.CabinetDetailView.as_view(), name="profile"),
    path('user/update/', cabinet_views.CabinetUpdateView.as_view(), name="profile_update"),

    path('tariff/index/', tariff_views.FlatTariffDetailView.as_view(), name="tariff_index"),

    path('master-request/index/', master_request_views.OwnerRequestsDetailView.as_view(), name="owner_requests_list"),
    path('', summary_views.summary, name="summary"),
]

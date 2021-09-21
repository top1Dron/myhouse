from myhouse_admin.models import (PaymentDetails, MainPage,
    ServicesPage, TariffPage, ContactsPage, AboutUsPage)


def load_settings(request):
    return {
        'main_page': MainPage.load(),
        'about_us_page': AboutUsPage.load(),
        'services_page': ServicesPage.load(),
        'tariff_page': TariffPage.load(),
        'contacts_page': ContactsPage.load(),
        'payment_details': PaymentDetails.load()
    }
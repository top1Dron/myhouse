from myhouse_admin.models import (PaymentDetails, MainPage,
    ServicesPage, TariffPage, ContactsPage, AboutUsPage)
from myhouse_admin.utils import db_utils


def load_settings(request):
    new_owners = db_utils.get_new_owners()

    return {
        'main_page': MainPage.load(),
        'about_us_page': AboutUsPage.load(),
        'services_page': ServicesPage.load(),
        'tariff_page': TariffPage.load(),
        'contacts_page': ContactsPage.load(),
        'payment_details': PaymentDetails.load(),
        'new_owners_count': new_owners.count(),
        'new_owners': new_owners,
    }
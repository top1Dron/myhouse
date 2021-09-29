from datetime import datetime as dt, date
import calendar
import io
import logging
import os
import xlsxwriter

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Model
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.template.loader import get_template
from django.urls.base import reverse_lazy
from django.utils.functional import wraps
from xhtml2pdf import pisa
import django_excel as excel

from . import db_utils


logger = logging.getLogger(__name__)


def get_current_datetime() -> str:
    t = dt.now()
    return f'{t:%d%m%y}'

def get_auto_id(model: Model):
    try:
        auto_id = f'{model.objects.all().order_by("-id").first().pk + 1:05d}'
    except AttributeError:
        auto_id = f'00001'
    return get_current_datetime() + auto_id

def get_dt_now_object():
    return dt.now()


def get_datetime_from_date_and_time(date, time):
    return dt.combine(date, time)


def permission_required(permission_number: str, login_url=reverse_lazy('myhouse_admin:admin_login')):
    return user_passes_test(lambda u: permission_number in u.employee.role.abilities, login_url=login_url)


class UserCheckMixin(object):
    user_check_failure_path = ''  # can be path, url name or reverse_lazy

    def check_user(self, user):
        return True
    
    def check_cabinet_user(self, request):
        return True

    def user_check_failed(self, request, *args, **kwargs):
        return redirect(self.user_check_failure_path)

    def dispatch(self, request, *args, **kwargs):
        if not self.owner_cabinet:
            if not self.check_user(request.user):
                return self.user_check_failed(request, *args, **kwargs)
        else:
            if not self.check_cabinet_user(request):
                return self.user_check_failed(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)


class PermissionRequiredMixin(UserCheckMixin):
    user_check_failure_path = reverse_lazy('myhouse_admin:admin_login')
    permission_required = None
    owner_cabinet = False

    def check_user(self, user):
        return self.permission_required in user.employee.role.abilities
    
    def check_cabinet_user(self, request):
        if 'owner_ID' in request.GET or hasattr(request.user, 'owner'):
            return True
        else:
            return False


class CabinetPermissionRequiredMixin:
    user_check_failure_path = reverse_lazy('users:login')
    
    def dispatch(self, request, *args, **kwargs):
        if 'owner_ID' in request.GET:
            return super().dispatch(request, *args, **kwargs)
        else:
            if hasattr(request.user, 'owner'):
                return super().dispatch(request, *args, **kwargs)
            else:
                return redirect(self.user_check_failure_path)


def owner_flat_required(view):
    @wraps(view)
    def inner(request, *args, **kwargs):
        user_check_failure_path = reverse_lazy('users:login')
        if 'owner_ID' in request.GET:
            owner = db_utils.get_owner_object_by_params(ID=request.GET['owner_ID'])
        else:
            if hasattr(request.user, 'owner'):
                owner = request.user.owner
            else:
                return redirect(user_check_failure_path)

        if len(owner.flats.all()) == 0:
            return redirect(user_check_failure_path)
            
        return view(request, *args, **kwargs)
    
    return inner

def get_month_range(month:str):
    _month, year = [int(i) for i in month.split('.')]
    start_day, end_day = calendar.monthrange(year, _month)
    return (date(year=year, month=_month, day=start_day), 
        date(year=year, month=_month, day=end_day))


def translate_month_to_ukr(date: str):
    month_en = ('January', 'Fabuary', 'March', 'April', 'May', 
        'June', 'July', 'August', 'September',
        'October', 'November', 'December')
    month_ua = ('Сiчень', 'Лютий', 'Березень', 'Квiтень', 'Трвавень', 
        'Червень', 'Липень', 'Серпень', 'Вересень',
        'Жовтень', 'Листопад', 'Грудень')
    for month in zip(month_en, month_ua):
        date = date.replace(month[0], month[1])
    return date


def export_models_to_excel(filename_start: str, Model):
    responce = None
    
    EXCEL_FILE_NAME = filename_start + '_' + dt.now().strftime("%Y%m%d_%H%M%S")
    try:
        data = Model.export_to_excel()
        responce = excel.make_response_from_array(data, 'xlsx', file_name=EXCEL_FILE_NAME)
    except Exception as error:
        try:
            data = Model.export_to_excel_one()
            responce = excel.make_response_from_array(data, 'xlsx', file_name=EXCEL_FILE_NAME)
        except:
            logger.error(f"Export database to excel failed: {str(error)}")
    return responce


def export_receipt_to_excel(filename_start, receipt: db_utils.Receipt, to_pdf=False):
    EXCEL_FILE_NAME = filename_start + '_' + dt.now().strftime("%Y%m%d_%H%M%S") + '.xlsx'

    buffer = io.BytesIO()
    workbook = xlsxwriter.Workbook(buffer)
    worksheet = workbook.add_worksheet()

    # set default row and column height and width
    worksheet.set_row(0, 25)
    worksheet.set_row(8, 60)
    worksheet.set_row(9, 25)
    worksheet.set_column('A:A', 15.5)
    worksheet.set_column('B:B', 15.3)
    worksheet.set_column('C:C', 9)
    worksheet.set_column('D:D', 15)
    worksheet.set_column('E:E', 12)
    worksheet.set_column('F:F', 10)
    worksheet.set_column('G:G', 6)
    worksheet.set_column('H:H', 25)
    worksheet.set_column('I:I', 5)
    worksheet.set_column('J:J', 6)
    worksheet.set_column('K:K', 22)

    font = workbook.add_format({'font_name': 'Arial', 'font_size': 14, 'valign': 'top', 'left': 2, 'top': 2, 'valign': 'top'})
    worksheet.merge_range('A1:A2',    'Отримувач/\nВиконувач', font)

    font = workbook.add_format({'font_name': 'Arial', 'font_size': 11, 'valign': 'top', 'top': 2, 'valign': 'top'})
    worksheet.merge_range('B1:G4', db_utils.get_payments_details().replace('\r', ''), font)

    font = workbook.add_format({'font_name': 'Arial', 'font_size': 14, 'valign': 'top', 'top': 2, 'valign': 'top'})
    worksheet.write('H1', '№ О/рахунку', font)
    
    font = workbook.add_format({'font_name': 'Arial', 'font_size': 16, 'valign': 'top', 'border': 2, 'bottom': 0, 'valign': 'top'})
    worksheet.merge_range('I1:K1', 'ПОВIДОМЛЕННЯ', font)
    
    font = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 14, 'border': 5 })
    worksheet.write('H2', receipt.flat.personal_account.uid if receipt.flat.personal_account else '', font)

    font = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 16, 'left': 5})
    worksheet.write('I2', '№', font)
    worksheet.write('I3', 'от', font)

    font = workbook.add_format({'left': 2})
    worksheet.write('A3', '', font)
    worksheet.write('A4', '', font)
    worksheet.write('A12', '', font)
    worksheet.write('A13', '', font)

    font = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 16, 'right': 2})
    worksheet.merge_range('J2:K2', f'{receipt.number}', font)
    worksheet.merge_range('J3:K3', receipt.creation_date.strftime('%d.%m.%Y'), font)

    for row in range(3, 9):
        worksheet.write(row, 8, '',  workbook.add_format({'left': 5}))
        worksheet.merge_range(row, 9, row, 10, '', workbook.add_format({'right': 5}))

    font = workbook.add_format({'font_name': 'Arial', 'font_size': 14, 'left': 2})
    worksheet.write('A5', 'Платник', font)
    worksheet.write('A6', 'Нараховано', font)
    worksheet.write('A7', 'Баланс О/р', font)
    worksheet.write('A14', 'Платник', font)
    worksheet.write('A15', 'Нараховано', font)
    worksheet.write('A16', 'Баланс О/р', font)

    font = workbook.add_format({'font_name': 'Arial', 'font_size': 14, 'bold': True})
    worksheet.merge_range('B5:G5', f'{receipt.flat.owner} {receipt.flat.floor.section.house.address} квартира {receipt.flat.number}', font)
    
    font = workbook.add_format({'font_name': 'Arial', 'font_size': 14})
    worksheet.write_number('B6', receipt.summary, font)
    worksheet.write_number('B7', receipt.flat.actual_balance, font)
    worksheet.write('C7', 'на', font)
    worksheet.merge_range('D7:E7', receipt.creation_date.strftime('%d.%m.%Y'), font)

    worksheet.write_number('B15', receipt.summary, font)
    worksheet.write_number('B16', receipt.flat.actual_balance, font)
    worksheet.write('C16', 'на', font)
    worksheet.merge_range('D16:E16', receipt.creation_date.strftime('%d.%m.%Y'), font)

    font = workbook.add_format({'font_name': 'Arial', 'font_size': 14, 'left': 2, 'top': 5, 'bottom': 5})
    worksheet.write('A8', 'ДО СПЛАТИ', font)

    font = workbook.add_format({'font_name': 'Arial', 'font_size': 14, 'top': 5, 'bottom': 5})
    worksheet.write_number('B8', receipt.summary, font)
    worksheet.write('C8', 'за', font)

    font = workbook.add_format({'font_name': 'Arial', 'font_size': 14, 'top': 5, 'bottom': 5, 'bold': True, 'right': 5})
    worksheet.merge_range('D8:E8', translate_month_to_ukr(receipt.end_date.strftime('%B %Y')), font)
    
    font = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'bottom': 5, 'valign': 'top'})
    worksheet.merge_range('F8:H9', 'С условиями приема банком суммы\nознакомлен и согласен\n________________\n(пiдпис платника)', font)
    worksheet.merge_range('A9:D9', '', workbook.add_format({'border': 5}))
    worksheet.write('E9', '', workbook.add_format({'bottom': 5}))

    font = workbook.add_format({'font_name': 'Arial', 'font_size': 14, 'valign': 'top', 'left': 2, 'valign': 'top'})
    worksheet.merge_range('A10:A11',    'Отримувач/\nВиконувач', font)
    
    font = workbook.add_format({'font_name': 'Arial', 'font_size': 11, 'valign': 'top', 'valign': 'top'})
    worksheet.merge_range('B10:G13', db_utils.get_payments_details().replace('\r', ''), font)
    font = workbook.add_format({'font_name': 'Arial', 'font_size': 14, 'valign': 'top', 'valign': 'top'})
    worksheet.write('H10', '№ О/рахунку', font)

    font = workbook.add_format({'font_name': 'Arial', 'font_size': 16, 'valign': 'top', 'border': 2, 'bottom': 0, 'top':5, 'valign': 'top'})
    worksheet.merge_range('I10:K10', 'КВIТАНЦIЯ', font)
    
    font = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 14, 'border': 5 })
    worksheet.write('H11', receipt.flat.personal_account.uid if receipt.flat.personal_account else '', font)
    
    font = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 16, 'left': 5})
    worksheet.write('I11', '№', font)
    worksheet.write('I12', 'от', font)

    font = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 16, 'right': 2})
    worksheet.merge_range('J11:K11', f'{receipt.number}', font)
    worksheet.merge_range('J12:K12', receipt.creation_date.strftime('%d.%m.%Y'), font)

    font = workbook.add_format({'font_name': 'Arial', 'font_size': 14, 'bold': True})
    worksheet.merge_range('B14:G14', f'{receipt.flat.owner} {receipt.flat.floor.section.house.address} квартира {receipt.flat.number}', font)
   
    font = workbook.add_format({'font_name': 'Arial', 'font_size': 14, 'left': 2, 'top': 5, 'bottom': 5})
    worksheet.write('A17', 'ДО СПЛАТИ', font)

    font = workbook.add_format({'font_name': 'Arial', 'font_size': 14, 'top': 5, 'bottom': 5})
    worksheet.write_number('B17', receipt.summary, font)
    worksheet.write('C17', 'за', font)

    font = workbook.add_format({'font_name': 'Arial', 'font_size': 14, 'top': 5, 'bottom': 5, 'bold': True, 'right': 5})
    worksheet.merge_range('D17:E17', translate_month_to_ukr(receipt.end_date.strftime('%B %Y')), font)

    for row in range(12, 17):
        worksheet.write(row, 8, '',  workbook.add_format({'left': 5}))
        worksheet.merge_range(row, 9, row, 10, '', workbook.add_format({'right': 5}))

    font = workbook.add_format({'font_name': 'Arial', 'font_size': 14, 'align': 'center', 'border': 5, 'right': 2})
    worksheet.merge_range('A18:B18', 'Услуга', font)
    worksheet.merge_range('C18:D18', 'Тариф', font)
    worksheet.merge_range('E18:F18', 'Ед.изм', font)
    worksheet.merge_range('G18:H18', 'Расход', font)
    worksheet.merge_range('I18:K18', 'Сумма, грн', font)
    
    row = 18
    for rs in receipt.r_services.all():
        worksheet.merge_range(row, 0, row, 1, rs.service.name, workbook.add_format({'font_name': 'Arial', 'font_size': 14, 'left': 2, 'right': 5}))
        worksheet.merge_range(row, 2, row, 3, f'{rs.unit_price:.2f}', workbook.add_format({'font_name': 'Arial', 'font_size': 14, 'left': 2, 'right': 5, 'align': 'right'}))
        worksheet.merge_range(row, 4, row, 5, rs.service.unit.name, workbook.add_format({'font_name': 'Arial', 'font_size': 14, 'left': 2, 'right': 5, 'align': 'right'}))
        worksheet.merge_range(row, 6, row, 7, f'{int(rs.consumption)}', workbook.add_format({'font_name': 'Arial', 'font_size': 14, 'left': 2, 'right': 5, 'align': 'right'}))
        worksheet.merge_range(row, 8, row, 10, f'{rs.total_price:.2f}', workbook.add_format({'font_name': 'Arial', 'font_size': 14, 'left': 2, 'right': 2, 'align': 'right'}))
        row += 1
    
    worksheet.merge_range(row, 0, row, 1, '', workbook.add_format({'left': 2, 'right': 5}))
    worksheet.merge_range(row, 2, row, 3, '', workbook.add_format({'left': 2, 'right': 5}))
    worksheet.merge_range(row, 4, row, 5, '', workbook.add_format({'left': 2, 'right': 5}))
    worksheet.merge_range(row, 6, row, 7, '', workbook.add_format({'left': 2, 'right': 5}))
    worksheet.merge_range(row, 8, row, 10, '', workbook.add_format({'left': 2, 'right': 2}))
    
    row += 1    
    worksheet.merge_range(row, 0, row, 1, '', workbook.add_format({'left': 2, 'right': 5, 'bottom':2}))
    worksheet.merge_range(row, 2, row, 3, '', workbook.add_format({'left': 2, 'right': 5, 'bottom':2}))
    worksheet.merge_range(row, 4, row, 5, '', workbook.add_format({'left': 2, 'right': 5, 'bottom':2}))
    worksheet.merge_range(row, 6, row, 7, 'РАЗОМ:', workbook.add_format({'font_name': 'Arial', 'font_size': 14, 'bottom':2, 'right': 5, 'align': 'right', 'bold': True}))
    worksheet.merge_range(row, 8, row, 10, f'{receipt.summary}', workbook.add_format({'font_name': 'Arial', 'font_size': 14, 'bottom':2, 'right': 2, 'align': 'right', 'bold': True}))

    workbook.close()

    if to_pdf:
        EXCEL_FILE_NAME = EXCEL_FILE_NAME.replace('xlsx', 'pdf')
    buffer.seek(0)

    return buffer, EXCEL_FILE_NAME


def fetch_pdf_resources(uri, rel):
    if uri.find(settings.MEDIA_URL) != -1:
        path = os.path.join(settings.BASE_DIR, uri.replace(settings.MEDIA_URL, 'media/'))
    elif uri.find(settings.STATIC_URL) != -1:
        path = os.path.join(settings.BASE_DIR, uri.replace(settings.STATIC_URL, 'static/'))
    else:
        path = None
    return path


def render_to_pdf(template_src, context_dict):
    filename = f'invoice_{context_dict.get("receipt").number}' + '_' + dt.now().strftime("%Y%m%d_%H%M%S") + '.pdf'
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.StringIO(html), dest=result, encoding='utf-8', link_callback=fetch_pdf_resources)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf'), filename
    return None, filename
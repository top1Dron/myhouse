import logging

from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods

from .process_singleton import ProcessSingletonModel
from myhouse_admin.forms.forms import MainPageForm, ServicesPageForm, TariffPageForm, ContactsPageForm, AboutUsPageForm, AboutUsPageImageForm, AboutUsPageAdditionalImageForm
from myhouse_admin.models import AboutUsPage, Document, MainPage, Block, ServicesPage, TariffPage, TariffImage, ContactsPage
from myhouse_admin.utils import db_utils
from myhouse_admin.utils.utils import permission_required


logger = logging.getLogger(__name__)


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@permission_required('11')
def main_page(request):
    process_singleton_model = ProcessSingletonModel(
        model=MainPage, 
        form_class=MainPageForm, 
        generic_model=Block,
        generic_form_prefix='blocks',
        generic_extra_forms=6,
        template_name='site_management/main_page.html',
        success_url=reverse_lazy('myhouse_admin:main_page'),
        request=request)
    
    redirect_available, form, blocks = process_singleton_model.get_filled_forms(
        post_dict=request.POST,
        files_dict=request.FILES,
        method=request.method
    )
    if redirect_available:
        return redirect(reverse_lazy('myhouse_admin:main_page'))
    else:
        return render(request, 'site_management/main_page.html', {
            'form': form,
            'blocks': blocks
        })


@permission_required('11')
@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
def services_page(request):
    process_singleton_model = ProcessSingletonModel(
        model=ServicesPage, 
        form_class=ServicesPageForm, 
        generic_model=Block,
        generic_form_prefix='blocks',
        generic_extra_forms=0,
        template_name='site_management/services_page.html',
        success_url=reverse_lazy('myhouse_admin:services_page'),
        request=request)
    
    redirect_available, form, blocks = process_singleton_model.get_filled_forms(
        post_dict=request.POST,
        files_dict=request.FILES,
        method=request.method
    )
    if redirect_available:
        return redirect(reverse_lazy('myhouse_admin:services_page'))
    else:
        return render(request, 'site_management/services_page.html', {
            'form': form,
            'blocks': blocks
        })


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@permission_required('11')
def tariff_page(request):
    process_singleton_model = ProcessSingletonModel(
        model=TariffPage, 
        form_class=TariffPageForm, 
        generic_model=TariffImage,
        generic_form_prefix='blocks',
        generic_extra_forms=0,
        template_name='site_management/tariff_page.html',
        success_url=reverse_lazy('myhouse_admin:tariff_page'),
        request=request)
    
    redirect_available, form, blocks = process_singleton_model.get_filled_forms(
        post_dict=request.POST,
        files_dict=request.FILES,
        method=request.method
    )
    if redirect_available:
        return redirect(reverse_lazy('myhouse_admin:tariff_page'))
    else:
        return render(request, 'site_management/tariff_page.html', {
            'form': form,
            'blocks': blocks
        })


@permission_required('11')
@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
def contacts_page(request):
    process_singleton_model = ProcessSingletonModel(
        model=ContactsPage, 
        form_class=ContactsPageForm,
        template_name='site_management/contacts_page.html',
        success_url=reverse_lazy('myhouse_admin:contacts_page'),
        request=request)
    
    redirect_available, form = process_singleton_model.get_filled_forms(
        post_dict=request.POST,
        method=request.method
    )
    if redirect_available:
        return redirect(reverse_lazy('myhouse_admin:contacts_page'))
    else:
        return render(request, 'site_management/contacts_page.html', {
            'form': form,
        })


@permission_required('11')
@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
def about_us_page(request):
    process_singleton_model = ProcessSingletonModel(
        model=AboutUsPage, 
        form_class=AboutUsPageForm,
        first_related_model_form=AboutUsPageImageForm,
        first_related_model_form_prefix='first_related',
        second_related_model_form=AboutUsPageAdditionalImageForm,
        second_related_model_form_prefix='second_related',
        first_related_model_in_formset=Document,
        first_related_model_in_formset_fields=('file', 'name'),
        template_name='site_management/about_us_page.html',
        success_url=reverse_lazy('myhouse_admin:about_us_page'),
        request=request)
    
    redirect_available, form, image_form, ad_image_form, document_formset = process_singleton_model.get_filled_forms(
        post_dict=request.POST,
        files_dict=request.FILES,
        method=request.method
    )
    if redirect_available:
        return redirect(reverse_lazy('myhouse_admin:about_us_page'))
    else:
        return render(request, 'site_management/about_us_page.html', {
            'form': form,
            'image_form': image_form,
            'ad_image_form': ad_image_form,
            'document_formset': document_formset
        })


@permission_required('11')
@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@require_http_methods(['DELETE'])
def delete_block(request, pk):
    block = db_utils.get_block_by_params(pk=pk)
    block.delete()
    return JsonResponse({})


@permission_required('11')
@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@require_http_methods(['DELETE'])
def delete_about_image(request, pk):
    image = db_utils.get_image_by_params(pk=pk)
    image.delete()
    return JsonResponse({})


@staff_member_required(login_url=reverse_lazy('myhouse_admin:admin_login'))
@require_http_methods(['DELETE'])
@permission_required('11')
def delete_about_ad_image(request, pk):
    image = db_utils.get_ad_image_by_params(pk=pk)
    image.delete()
    return JsonResponse({})
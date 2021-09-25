import {add_form, getCookie, deleteObject } from '../../services.js'

$(document).ready(function(){
    $('#add_unit').click(function(e){
        add_form('id_unit-TOTAL_FORMS', 'all_unit', 'empty_unit_form');
    });

    $('#add_service').click(function(e){
        add_form('id_service-TOTAL_FORMS', 'all_service', 'empty_service_form');
    });

    $('#nav_unit').click(function(e){
        if($('#nav_service').hasClass('active')){
            $('#nav_service').removeClass('active');
            $('#tab_service').removeClass('active').removeClass('show');
            $('#nav_unit').addClass('active');
            $('#tab_unit').addClass('active').addClass('show');
        }
    });

    $('#nav_service').click(function(e){
        if($('#nav_unit').hasClass('active')){
            $('#nav_unit').removeClass('active');
            $('#tab_unit').removeClass('active').removeClass('show');
            $('#nav_service').addClass('active');
            $('#tab_service').addClass('active').addClass('show');
        }
    });

    window.deleteUnit = deleteUnit;
    window.deleteService = deleteService;
})

function deleteUnit(button, totalFormsId, update=false){
    if(!update){
        $(button).parent().parent().remove();
    }else{
        deleteObject(button, getCookie('csrftoken'), 
        'Вы уверены, что хотите удалить данные этой единицы измерения из базы данных?',
        'Данные успешно удалены!');
    }
}

function deleteService(button, totalFormsId, update=false){
    if(!update){
        $(button).parent().parent().parent().remove();
    }else{
        deleteObject(button, getCookie('csrftoken'), 
        'Вы уверены, что хотите удалить данные этой единицы измерения из базы данных?',
        'Данные успешно удалены!');
    }
}
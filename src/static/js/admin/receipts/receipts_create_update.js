import {add_form, getCookie, deleteObject, service_onchange_ajax } from '../../services.js'

$(document).ready(function(){
    
    $('#creationdate').datetimepicker({
        autoclose: true,
        locale: 'ru',
        format:'DD.MM.YYYY',
    });

    $('#fromdate').datetimepicker({
        autoclose: true,
        locale: 'ru',
        format:'DD.MM.YYYY',
    });

    $('#todate').datetimepicker({
        autoclose: true,
        locale: 'ru',
        format:'DD.MM.YYYY',
    });

    $("#id_house").change(function () {
        var url = $("#id_house").attr("data-house-sections-url");
        var houseId = $(this).val();

        $.ajax({
            url: url,
            data: {
                'house': houseId
            },
            success: function (data) {
                $("#id_section").html(data);
                $.ajax({
                    url: $("#id_house").attr("data-empty-flats"),
                    data: {},
                    success: function (data) {
                        $("#id_flat").html(data);
                    }
                });
            }
        });
    });

    $('#id_section').change(function(){
        var sectionId = $("#id_section").val();
        var url = $("#id_section").attr("data-section-flat-url");
        var data = {};
        if (url != undefined){
            data = {
                'section': sectionId
            }
        } else{
            url =  $("#id_section").attr("data-section-flat-update-url");
            data = {
                'section': sectionId,
                'flat': $("#id_flat").val(),
            }
        }
        $.ajax({
            url: url,
            data: data,
            success: function (data) {
                $("#id_flat").html(data);
            }
        });
    });

    $('#id_flat').change(function(){
        var url = $(this).attr("data-flat-details-url");
        var flatId = $(this).val();

        $.ajax({
            url: url,
            data: {
                'flat': flatId
            },
            success: function (data) {
                $(`#id_flat_owner`).html(data['flat_owner_name']);
                $(`#id_flat_owner_phone`).html(data['flat_owner_phone']);
                $(`#id_flat_tariff`).html(data['flat_tariff']);
            }
        });
    });

    $('#add_service').click(function(e){
        var total_forms = add_form('id_service-TOTAL_FORMS', 'id_receipt_services_body', 'empty_service_form');
        var current_form = total_forms - 1;

        $(`#id_service-${current_form}-consumption, 
            #id_service-${current_form}-unit_price, 
            #id_service-${current_form}-service,
            #id_service-${current_form}-unit,
            #id_service-${current_form}-total_price`).prop('required',true);
        
        $(`#id_service-${current_form}-consumption, #id_service-${current_form}-unit_price`).change(function(){
            var total = (parseFloat($(`#id_service-${current_form}-consumption`).val()) 
                * parseFloat($(`#id_service-${current_form}-unit_price`).val())).toFixed(2);
            $(`#id_service-${current_form}-total_price`).val(total);
            calculateSum(total_forms);
        });
        $(`#id_service-${current_form}-total_price`).change(function(){
            calculateSum(total_forms);
        });

        $(`#id_service-${current_form}-service`).change(function(){
            service_onchange_ajax(`id_service-${current_form}-service`, `id_service-${current_form}-unit`, true);
        });
    });

    add_formset_functionality('id_service-TOTAL_FORMS');

    window.deleteService = deleteService;
})

function add_formset_functionality(total_forms_id){
    var total_forms = parseInt($(`#${total_forms_id}`).val());
    for(var ind=0; ind<total_forms; ind++){
        $(`#id_service-${ind}-consumption, 
            #id_service-${ind}-unit_price, 
            #id_service-${ind}-service,
            #id_service-${ind}-unit,
            #id_service-${ind}-total_price`).prop('required',true);
        
        $(`#id_service-${ind}-consumption, #id_service-${ind}-unit_price`).change(generate_consumption_unit_price_change_handler(ind, total_forms));
        $(`#id_service-${ind}-total_price`).change(function(){
            calculateSum(total_forms);
        });

        $(`#id_service-${ind}-service`).change(generate_service_change_handler(ind));
    }
}

function generate_service_change_handler( j ) {
    return function() {
        service_onchange_ajax(`id_service-${j}-service`, `id_service-${j}-unit`, true);
    };
}

function generate_consumption_unit_price_change_handler( j, total_forms) {
    return function() {
        var total = (parseFloat($(`#id_service-${j}-consumption`).val()) 
            * parseFloat($(`#id_service-${j}-unit_price`).val())).toFixed(2);
        $(`#id_service-${j}-total_price`).val(total);
        calculateSum(total_forms);
    };
}

function calculateSum(total_forms){
    var total_sum = 0.0;
    for(var i = 0; i < total_forms; i++){
        if(!isNaN(parseFloat($(`#id_service-${i}-total_price`).val()))){
            total_sum += parseFloat($(`#id_service-${i}-total_price`).val());
        }
    }
    if(isNaN(total_sum)){
        total_sum = 0.0;
    }
    $('#id_summary').val(total_sum.toFixed(2));
    $('#id_summary_display').html(total_sum.toFixed(2));
}

function deleteService(button, totalFormsId, update=false){
    if(!update){
        $(button).parent().parent().remove();
        calculateSum(parseInt($(`#${totalFormsId}`).val()));
    }else{
        deleteObject(button, getCookie('csrftoken'), 
        'Вы уверены, что хотите удалить выбранные данные из базы данных?',
        'Данные успешно удалены!');
    }
}
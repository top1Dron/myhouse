import {add_form, getCookie, deleteObject, service_onchange } from '../../services.js'

$(document).ready(function(){
    $('#add_service').click(function(e){
        add_form('id_service-TOTAL_FORMS', 'tariff_services', 'empty_service_form');
        var form_ind = $(`#id_service-TOTAL_FORMS`).val() - 1;
        var service_id = 'id_service-TOTAL_FORMS'.replace('TOTAL_FORMS', `${form_ind}-service`);
        var unit_id = `${form_ind}-serviceunit-name`;
        service_onchange(service_id, unit_id);
    });

    window.deleteService = deleteService;
})

function deleteService(button, totalFormsId, update=false){
    if(!update){
        $(button).parent().parent().parent().parent().parent().parent().remove();
        var form_idx = $(`#${totalFormsId}`).val();
        $(`#${totalFormsId}`).val(parseInt(form_idx) - 1);
    }else{
        deleteObject(button, getCookie('csrftoken'), 
        'Вы уверены, что хотите удалить данные этой услуги тарифа из базы данных?',
        'Данные успешно удалены!');
    }
}
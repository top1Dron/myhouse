import {add_form, getCookie } from '../../services.js'

$(document).ready(function(){
    $('#add_section').click(function(e){
        add_form('id_section_set-TOTAL_FORMS', 'sections', 'empty_sections_form');
    });

    $('#add_employee').click(function(e){
        add_form('id_employee_set-TOTAL_FORMS', 'employee', 'empty_employee_form');
        $('.employee-select').change(function(e){
            e.preventDefault();
            var selectField = this;
            var roleUrl = '/myhouse-admin/user-admin/get-employee-role/' + $(this).val() + '/';
            $.ajax({
                url: roleUrl,
                type: 'GET',
                data: {},
                success: function(resp){
                    var roleCol = $(selectField).parent().parent().parent().children('.col-lg-5').children('.form-group').children('.role');
                    $(roleCol).val(resp['role']);
                }
            });
        });
    });

    $('#section-tab').click(function(e){
        if($('#employee-tab').hasClass('active')){
            $('#employee-tab').removeClass('active').removeAttr('aria-current');
            $('#section-tab').addClass('active').attr('aria-current', 'page');
            $('.employee-block').removeClass('d-block').addClass('d-none');
            $('.sections-block').removeClass('d-none').addClass('d-block');
        }
    });

    $('#employee-tab').click(function(e){
        if($('#section-tab').hasClass('active')){
            $('#section-tab').removeClass('active').removeAttr('aria-current');
            $('#employee-tab').addClass('active').attr('aria-current', 'page');
            $('.sections-block').removeClass('d-block').addClass('d-none');
            $('.employee-block').removeClass('d-none').addClass('d-block');
        }
    });
    
    window.deleteSection = deleteSection;
    window.deleteHouseEmployee = deleteHouseEmployee;
})

function deleteSection(button, totalFormsId, update=false, form_ind=-1, sectionId=-1){
    if(!update){
        $(button).parent().parent().remove();
    }else{
        var delete_form = totalFormsId.replace('TOTAL_FORMS', `${form_ind}-DELETE`);
        $(`#${delete_form}`).attr('checked', true);
        $(button).parent().parent().removeClass('d-flex');
        $(button).parent().parent().addClass('d-none');
        $('#id_deleted_sections').val($('#id_deleted_sections').val() + `${sectionId} `);
    }
    var form_idx = $(`#${totalFormsId}`).val();
    $(`#${totalFormsId}`).val(parseInt(form_idx) - 1);
}

function deleteHouseEmployee(button){
    $(button).parent().parent().remove();
    var deleteHouseEmployeeUrl = $(button).attr('delete-url');
    $.ajax({
        url: deleteHouseEmployeeUrl,
        type: 'DELETE',
        data: {},
        beforeSend: function (xhr) {
            xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
        },
        success: function(resp){
        }
    });
}
import { updateURLParameter, deleteObject, getCookie } from '../../services.js'

$(document).ready(function(){
    if($('#id_filtered_role').val() != '1'){
        $("#id_role").prop("selectedIndex", -1);
    }
    if($('#id_filtered_status').val() != '1'){
        $("#id_status").prop("selectedIndex", -1);
    }
    $('#id_role').change(function(e){
        document.location.href = updateURLParameter(window.location.search, 'role', $('#id_role').val());
    });
    $('#id_status').change(function(e){
        document.location.href = updateURLParameter(window.location.search, 'status', $('#id_status').val());
    });
    $('#id_full_name_search_field').on('keydown', function(e){
        if (e.key == 'Enter'){
            document.location.href = updateURLParameter(
                window.location.search, 
                'full_name', 
                document.getElementById('id_full_name_search_field').value);
        }
    });
    $('#id_phone_number_search_field').on('keydown', function(e){
        if (e.key == 'Enter'){
            document.location.href = updateURLParameter(
                window.location.search, 
                'phone_number', 
                document.getElementById('id_phone_number_search_field').value);
        }
    });
    $('#id_email_search_field').on('keydown', function(e){
        if (e.key == 'Enter'){
            document.location.href = updateURLParameter(
                window.location.search, 
                'email', 
                document.getElementById('id_email_search_field').value);
        }
    });
    $('.delete-employee-button').click(function(e){
        e.stopPropagation();
        deleteObject(this, getCookie('csrftoken'), 
            'Вы уверены, что хотите удалить данные этого пользователя из базы данных?',
            'Данные о пользователе удалены успешно!')
    });
    $('tr[data-href]').on("click", function() {
        document.location = $(this).data('href');
    });
})
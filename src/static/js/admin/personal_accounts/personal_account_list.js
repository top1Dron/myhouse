import { init_datatable, deleteObject, getCookie, updateURLParameter } from '../../services.js'

$(document).ready(function(){
    $('.delete-personal_account-button').click(function(e){
        e.stopPropagation();
    });
    
    $('tr[data-href]').on("click", function() {
        document.location = $(this).data('href');
    });

    init_datatable('id_pa_table', [0, 2], [3, 4, 5], [1]);

    $('#id_pa_table_filter').hide();

    $('.delete-personal_account-button').click(function(e){
        deleteObject(this, getCookie('csrftoken'), 
            'Вы уверены, что хотите удалить данные этого лицевого счета из базы данных?',
            'Лицевой счёт удален успешно!')
    });

    $('#id_search_debtors').val($('#id_search_debtors').attr("current-val"));

    $('#id_search_debtors').change(function(){
        document.location.href = updateURLParameter(
            window.location.search, 
            'has_debt', 
            $('#id_search_debtors').val());
    });
})
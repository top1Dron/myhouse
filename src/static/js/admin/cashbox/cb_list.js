import { deleteObject, getCookie, init_datatable } from '../../services.js'

$(document).ready(function(){
    $('.delete-cb_record-button').click(function(e){
        e.stopPropagation();
    });
    
    $('tr[data-href]').on("click", function() {
        document.location = $(this).data('href');
    });

    init_datatable('id_cashbox_table', [0, 1, 5], [2, 3, 4], [6]);

    $('#id_cashbox_table_filter').hide();

    $('.delete-cb_record-button').click(function(e){
        deleteObject(this, getCookie('csrftoken'), 
            'Вы уверены, что хотите удалить данные этой записи из базы данных?',
            'Данные о записи удалены успешно!')
    });
})
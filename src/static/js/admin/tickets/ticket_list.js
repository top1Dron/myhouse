import { init_datatable, deleteObject, getCookie } from '../../services.js'

$(document).ready(function(){
    $('.delete-ticket-button').click(function(e){
        e.stopPropagation();
    });
    
    $('tr[data-href]').on("click", function() {
        document.location = $(this).data('href');
    });

    init_datatable('id_ticket_table', [0, 1, 3, 4, 6], [2, 5, 7], [8]);

    $('#id_ticket_table_filter').hide();

    $('.delete-ticket-button').click(function(e){
        deleteObject(this, getCookie('csrftoken'), 
            'Вы уверены, что хотите удалить выбранные данные?',
            'Данные удалены успешно!')
    });
})
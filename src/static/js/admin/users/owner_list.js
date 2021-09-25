import { init_datatable, deleteObject, getCookie } from '../../services.js'

$(document).ready(function(){
    $('.delete-owner-button').click(function(e){
        e.stopPropagation();
    });
    
    $('tr[data-href]').on("click", function() {
        document.location = $(this).data('href');
    });

    $('.delete-owner-button').click(function(e){
        deleteObject(this, getCookie('csrftoken'), 
            'Вы уверены, что хотите отключить этого пользователя?',
            'Пользователь отключен!')
    });

    init_datatable('id_owner_table', [0, 1, 2, 3, 5, 6], [4], [7]);

    $('#id_owner_table_filter').hide();
})
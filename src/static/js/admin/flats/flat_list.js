import { deleteObject, getCookie, init_datatable } from '../../services.js'

$(document).ready(function(){
    $('.delete-flat-button').click(function(e){
        e.stopPropagation();
    });
    
    $('tr[data-href]').on("click", function() {
        document.location = $(this).data('href');
    });

    init_datatable('id_flat_table', [0], [1, 2, 3, 4], []);

    $('#id_flat_table_filter').hide();

    $('.delete-flat-button').click(function(e){
        deleteObject(this, getCookie('csrftoken'), 
            'Вы уверены, что хотите удалить данные этой квартиры из базы данных?',
            'Данные о квартире удалены успешно!')
    })
})
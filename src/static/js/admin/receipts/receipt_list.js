import { init_datatable, deleteObject, getCookie } from '../../services.js'

$(document).ready(function(){
    $('tr[data-href]').on("click", function() {
        document.location = $(this).data('href');
    });

    init_datatable('id_receipts_table', [1, 3, 4], [5, 6, 7], [2]);

    $('#id_receipts_table_filter').hide();

    $('.delete-receipt-button').click(function(e){
        deleteObject(this, getCookie('csrftoken'), 
            'Вы уверены, что хотите удалить данные этой квитанции из базы данных?',
            'Квитанция удалена успешно!')
    });
})
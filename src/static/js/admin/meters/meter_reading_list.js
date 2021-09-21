import { init_datatable, deleteObject, getCookie } from '../../services.js'

$(document).ready(function(){
    $('tr[data-href]').on("click", function() {
        document.location = $(this).data('href');
    });

    init_datatable('id_meter_table', [2], [0, 1, 3], []);

    $('#id_meter_table_filter').hide();

    init_datatable('id_meter_reading_table', [0, 2, 6], [4, 5, 7], [1]);

    $('#id_meter_reading_table_filter').hide();

    $('.delete-meter-button').click(function(e){
        deleteObject(this, getCookie('csrftoken'), 
            'Вы уверены, что хотите удалить данные этого показания счетчика из базы данных?',
            'Показания счетчика удалены успешно!')
    });
})
import { deleteObject, getCookie, init_datatable, updateURLParameter } from '../../services.js'

$(document).ready(function(){
    $('.delete-cb_record-button').click(function(e){
        e.stopPropagation();
    });
    
    $('tr[data-href]').on("click", function() {
        document.location = $(this).data('href');
    });

    init_datatable('id_cashbox_table', [0, 5], [2, 3, 4], [6]);

    $('#id_cashbox_table_filter').hide();

    $('.delete-cb_record-button').click(function(e){
        deleteObject(this, getCookie('csrftoken'), 
            'Вы уверены, что хотите удалить данные этой записи из базы данных?',
            'Данные о записи удалены успешно!')
    });

    $('#reservation').daterangepicker({
        autoclose: true,
        locale: {
            format: 'DD.MM.YYYY',
            "applyLabel": "Ок",
            "cancelLabel": "Отмена",
            "fromLabel": "От",
            "toLabel": "До",
            "customRangeLabel": "Произвольный",
            "daysOfWeek": [
                "Вс",
                "Пн",
                "Вт",
                "Ср",
                "Чт",
                "Пт",
                "Сб"
            ],
            "monthNames": [
                "Январь",
                "Февраль",
                "Март",
                "Апрель",
                "Май",
                "Июнь",
                "Июль",
                "Август",
                "Сентябрь",
                "Октябрь",
                "Ноябрь",
                "Декабрь"
            ],
            firstDay: 1
          }
    });

    $('#reservation').change(function(){
        var search_url = updateURLParameter(
            window.location.search, 
            'start_date', 
            $('#reservation').data('daterangepicker').startDate.format('YYYY-MM-DD'));
        document.location.href = updateURLParameter(
            search_url, 
            'end_date', 
            $('#reservation').data('daterangepicker').endDate.format('YYYY-MM-DD'));
    });
})
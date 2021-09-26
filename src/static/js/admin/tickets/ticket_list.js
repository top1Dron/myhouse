import { init_datatable, deleteObject, getCookie, updateURLParameter } from '../../services.js'

$(document).ready(function(){
    $('.delete-ticket-button').click(function(e){
        e.stopPropagation();
    });
    
    $('tr[data-href]').on("click", function() {
        document.location = $(this).data('href');
    });

    init_datatable('id_ticket_table', [0, 3, 4, 6], [2, 5, 7], [8]);

    $('#id_ticket_table_filter').hide();

    $('.delete-ticket-button').click(function(e){
        deleteObject(this, getCookie('csrftoken'), 
            'Вы уверены, что хотите удалить выбранные данные?',
            'Данные удалены успешно!')
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
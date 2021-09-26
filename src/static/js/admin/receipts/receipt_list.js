import { init_datatable, deleteObject, getCookie, updateURLParameter } from '../../services.js'

$(document).ready(function(){

    $('.icheck-primary, .delete-receipt-button').click(function(e){
        e.stopPropagation();
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

    $('#id_monthPicker').datetimepicker({
        autoclose: true,
        locale: 'ru',
        format:'MM.YYYY',
    });

    $("#id_monthPicker").on("change.datetimepicker", function() {
        document.location.href = updateURLParameter(
            window.location.search, 
            'month', 
            $('#id_monthPicker_input').val());
    });
    
    $('tr[data-href]').on("click", function() {
        document.location = $(this).data('href');
    });

    init_datatable('id_receipts_table', [1], [5, 6, 7], [2]);

    $('#id_receipts_table_filter').hide();

    $('.delete-receipt-button').click(function(e){
        deleteObject(this, getCookie('csrftoken'), 
            'Вы уверены, что хотите удалить данные этой квитанции из базы данных?',
            'Квитанция удалена успешно!')
    });

    $("#id_selection_all").click(function(){
        $('input[name=receipts_check]').not(this).prop('checked', this.checked);
    });

    $("#id_delete_many").click(function(){
        var ids = [];
        $('input[name="receipts_check"]:checked').each(function() { 
            var v = $(this).val();
            ids.push(v);
        });

        var url = $(this).attr('delete-url');
        
        if (ids.length) {
            if (confirm('Данные будут удалены. Продолжить?')) {
                $.ajax({
                    url: url,
                    data: {'ids': ids},
                    type: 'POST',
                    beforeSend: function (xhr) {
                        xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
                    },
                    success: function (data) {
                        location.reload();
                    },
                    error: function (data) {
                        console.log('ERROR');
                        console.log(data);
                    },
                });
            }
        }
    });
})
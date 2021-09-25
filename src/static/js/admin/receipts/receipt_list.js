import { init_datatable, deleteObject, getCookie } from '../../services.js'

$(document).ready(function(){

    $('.icheck-primary, .delete-receipt-button').click(function(e){
        e.stopPropagation();
    });

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
import { init_datatable, getCookie } from '../../services.js'

$(document).ready(function(){

    $('tr input[name="message_check"]').click(function(e){
        e.stopPropagation();
    });

    $('tr[data-href]').on("click", function() {
        document.location = $(this).data('href');
    });

    init_datatable('id_message_table', [], [], []);

    $('input[aria-controls="id_message_table"]').addClass('form-control').attr('placeholder', 'Поиск');
    $('#id_message_table_filter').addClass('mr-2').addClass('float-right').addClass('mt-2');

    $("#id_selection_all").click(function(){
        $('input[name=message_check]').not(this).prop('checked', this.checked);
    });

    $("#id_delete_many").click(function(){
        var ids = [];
        $('input[name="message_check"]:checked').each(function() { 
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
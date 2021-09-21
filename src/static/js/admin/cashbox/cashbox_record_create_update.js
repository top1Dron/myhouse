import { deleteObject, getCookie } from '../../services.js'

$(document).ready(function () {
    $('#recorddate').datetimepicker({
        autoclose: true,
        locale: 'ru',
        format:'DD.MM.YYYY',
    });

    $("#id_owner").change(function () {
        var url = $("#id_owner").attr("data-owner-paccounts-url");
        var ownerId = $(this).val();

        $.ajax({
            url: url,
            data: {
                'owner': ownerId
            },
            success: function (data) {
                $("#id_personal_account").html(data);
            }
        });
    });

    $('.delete-cb_record-button').click(function(e){
        deleteObject(this, getCookie('csrftoken'), 
            'Вы уверены, что хотите удалить данные этой записи из базы данных?',
            'Данные о записи удалены успешно!')
    });
});
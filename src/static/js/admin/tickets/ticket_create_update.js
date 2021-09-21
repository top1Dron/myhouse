$(document).ready(function () {
    $('#convenientdate').datetimepicker({
        autoclose: true,
        locale: 'ru',
        format:'DD.MM.YYYY',
    });

    $('#convenienttime').datetimepicker({
        autoclose: true,
        locale: 'ru',
        format:'HH:mm',
    });

    $(`#id_comment`).summernote({
        height: '200px',
    });

    $("#id_owner").change(function () {
        var url = $("#id_owner").attr("data-owner-flats-url");
        var ownerId = $(this).val();

        $.ajax({
            url: url,
            data: {
                'owner': ownerId
            },
            success: function (data) {
                $("#id_flat").html(data);
            }
        });
    });
});
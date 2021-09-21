$(document).ready(function () {
    $('#readingdate').datetimepicker({
        autoclose: true,
        locale: 'ru',
        format:'DD.MM.YYYY',
    });

    $("#id_house").change(function () {
        var url = $("#id_house").attr("data-house-sections-url");
        var houseId = $(this).val();

        $.ajax({
            url: url,
            data: {
                'house': houseId
            },
            success: function (data) {
                $("#id_section").html(data);
                $.ajax({
                    url: $("#id_house").attr("data-empty-flats"),
                    data: {},
                    success: function (data) {
                        $("#id_flat").html(data);
                    }
                });
            }
        });
    });

    $('#id_section').change(function(){
        var sectionId = $("#id_section").val();
        var url = $("#id_section").attr("data-section-flats-url");
        var data = {};
        if (url != undefined){
            data = {
                'section': sectionId
            }
        } else{
            url =  $("#id_section").attr("data-section-flats-update-url");
            data = {
                'section': sectionId,
                'flat': $("#id_flat").val(),
            }
        }
        $.ajax({
            url: url,
            data: data,
            success: function (data) {
                $("#id_flat").html(data);
            }
        });
    });
});
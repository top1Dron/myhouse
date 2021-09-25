$(document).ready(function(){
    $('#id_body').summernote({
        height: '200px',
        placeholder: "Текст сообщения:",
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
                $("#id_section").html(data.replace('Выберите', 'Всем'));
                $.ajax({
                    url: $("#id_house").attr("data-empty-flats"),
                    data: {},
                    success: function (data) {
                        $("#id_floor").html(data.replace('Выберите', 'Всем'));
                        $("#id_flat").html(data.replace('Выберите', 'Всем'));
                    }
                });
            }
        });
    });

    $('#id_section').change(function(){
        var url = $("#id_section").attr("data-section-floors-url");
        var sectionId = $("#id_section").val();

        $.ajax({
            url: url,
            data: {
                'section': sectionId
            },
            success: function (data) {
                $("#id_floor").html(data.replace('Выберите', 'Всем'));
                $.ajax({
                    url: $("#id_house").attr("data-empty-flats"),
                    data: {},
                    success: function (data) {
                        $("#id_flat").html(data.replace('Выберите', 'Всем'));
                    }
                });
            }
        });
    });

    $('#id_floor').change(function(){
        var url = $("#id_floor").attr("data-floor-flats-url");
        var floorId = $("#id_floor").val();

        $.ajax({
            url: url,
            data: {
                'floor': floorId
            },
            success: function (data) {
                $("#id_flat").html(data.replace('Выберите', 'Всем'));
            }
        });
    });
})
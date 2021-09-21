import {add_form, getCookie } from '../../services.js'

$(document).ready(function(){
    
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
                        $("#id_floor").html(data);
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
            $("#id_floor").html(data);
        }
        });
    });
})
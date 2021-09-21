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
                        $("#id_flat").html(data);
                    }
                });
            }
        });
    });

    $('#id_section').change(function(){
        var sectionId = $("#id_section").val();
        var url = $("#id_section").attr("data-section-flat-url");
        var data = {};
        if (url != undefined){
            data = {
                'section': sectionId
            }
        } else{
            url =  $("#id_section").attr("data-section-flat-update-url");
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

    $('#id_flat').change(function(){
        var url = $(this).attr("data-flat-details-url");
        var flatId = $(this).val();

        $.ajax({
            url: url,
            data: {
                'flat': flatId
            },
            success: function (data) {
                $(`#id_flat_owner`).html(data['flat_owner_name']);
                $(`#id_flat_owner_phone`).html(data['flat_owner_phone']);
            }
        });
    });
})
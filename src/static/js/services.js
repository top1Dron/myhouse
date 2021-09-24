export function updateURLParameter(url, param, paramVal)
{
    var TheAnchor = null;
    var newAdditionalURL = "";
    var tempArray = url.split("?");
    var baseURL = tempArray[0];
    var additionalURL = tempArray[1];
    var temp = "";

    if (additionalURL) 
    {
        var tmpAnchor = additionalURL.split("#");
        var TheParams = tmpAnchor[0];
            TheAnchor = tmpAnchor[1];
        if(TheAnchor)
            additionalURL = TheParams;

        tempArray = additionalURL.split("&");

        for (var i=0; i<tempArray.length; i++)
        {
            if(tempArray[i].split('=')[0] != param)
            {
                newAdditionalURL += temp + tempArray[i];
                temp = "&";
            }
        }        
    }
    else
    {
        var tmpAnchor = baseURL.split("#");
        var TheParams = tmpAnchor[0];
            TheAnchor  = tmpAnchor[1];

        if(TheParams)
            baseURL = TheParams;
    }

    if(TheAnchor)
        paramVal += "#" + TheAnchor;

    var rows_txt = "";
    if (paramVal){
        rows_txt += temp + "" + param + "=" + paramVal;
    }
    
    return baseURL + "?" + newAdditionalURL + rows_txt;
}

export function getCookie(name) {

    var matches = document.cookie.match(new RegExp(
    "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
    ))
    return matches ? decodeURIComponent(matches[1]) : undefined
}

export function deleteObject(button, csrf_token, 
    delete_confirm_message='Вы уверены, что хотите удалить данные этого объекта из базы данных?', 
    delete_success_message="Данные об объекте удалены"){
    
    if(confirm(delete_confirm_message)){
        var deleteUrl = $(button).attr("delete-url");
        $.ajax({
            url: deleteUrl,
            type: 'DELETE',
            data: {},
            beforeSend: function (xhr) {
                xhr.setRequestHeader('X-CSRFToken', csrf_token);
            },
            success: function(resp){
                alert(delete_success_message);
                window.location.reload();
            }
        });
    }

    // Swal.fire({
    //     title: delete_confirm_message,
    //     text: "Отмена действия невозможна",
    //     icon: 'warning',
    //     showCancelButton: true,
    //     confirmButtonColor: '#3085d6',
    //     cancelButtonColor: '#d33',
    //     confirmButtonText: 'Да, удалить!',
    //     cancelButtonText: 'Нет, отменить!',
    //     }).then((result) => {
    //         if (result.isConfirmed) {
    //             var deleteUrl = $(button).attr("delete-url");
    //             $.ajax({
    //                 url: deleteUrl,
    //                 type: 'DELETE',
    //                 data: {},
    //                 beforeSend: function (xhr) {
    //                     xhr.setRequestHeader('X-CSRFToken', csrf_token);
    //                 },
    //                 success: function(resp){
    //                     Swal.fire(
    //                         'Удалено!',
    //                         delete_success_message,
    //                         'success'
    //                     )
    //                     window.location.reload();
    //                 }
    //             });
    //         }
    //     })
}

export function add_form(totalFormsId, factoryBlockId, emptyFormId, ){
    var form_idx = $(`#${totalFormsId}`).val();
    $(`#${factoryBlockId}`).append($(`#${emptyFormId}`).html().replace(/__prefix__/g, form_idx).replace(/__prefix1__/g, parseInt(form_idx) + 1));
    var totalForms = parseInt(form_idx) + 1;
    $(`#${totalFormsId}`).val(totalForms);
    return totalForms;
}

export function extractContent(s) {
    var span = document.createElement('span');
    span.innerHTML = s;
    return span.textContent || span.innerText;
}

export function service_onchange_ajax(serviceId, unitId, select=false){
    var url = $(`#${serviceId}`).attr("get-service-unit-url");
    var servicePk = $(`#${serviceId}`).val();

    $.ajax({
        url: url,
        type: 'GET',
        data: {
            'service_pk': servicePk
        },
        success: function (data) {
            if(select){
                $(`#${unitId}`).val(data['unit_id']);
            }
            else{
                $(`#${unitId}`).val(data['unit_name']);
            }
        }
    });
}

export function service_onchange(serviceId, unitId, select=false){
    $(`#${serviceId}`).change(function(){
        service_onchange_ajax(serviceId, unitId, select=false);
    });
}

export function init_datatable(table_id, search_text_array, simple_select_array, html_values_select_array){
    $(`#${table_id}`).DataTable( {
        initComplete: function () {
            this.api().columns(simple_select_array).every( function () {
                var column = this;
                var select = $('<select class="form-control"><option value=""></option></select>')
                    .appendTo( $(column.header()).empty() )
                    .on( 'change', function () {
                        var val = $.fn.dataTable.util.escapeRegex(
                            $(this).val()
                        );
 
                        column
                            .search( val ? '^'+val+'$' : '', true, false )
                            .draw();
                    } );
 
                column.data().unique().sort().each( function ( data, index ) {
                    select.append("<option value='" + data + "'>" + data + "</option>")
                });
            });
            this.api().columns(html_values_select_array).every( function () {
                var column = this;
                var select = $("<select class='form-control'><option value=''></option></select>")
                    .appendTo( $(column.header()).empty() )
                    .on( 'change', function () {
                        var val = $.fn.dataTable.util.escapeRegex(
                            $(this).val()
                        );
 
                        column
                            .search( val ? '^'+val+'$' : '', true, false )
                            .draw();
                    } );
 
                column.data().unique().sort().each( function ( data, index ) {
                    var val = extractContent(data);
                    select.append("<option value='" + val + "'>" + val + "</option>")
                });
            });
            this.api().columns(search_text_array).every( function () {
                var column = this;
                var input = $('<input type="text" class="form-control" />')
                    .appendTo( $(column.header()).empty() )
                    .on('keyup change', function () {
                        column
                            .search( this.value )
                            .draw();
                });
            });
        },
        info: false,
        lengthChange: false,
        searching: true,
        ordering: false,
        paging: false,
        responsive: true,
    });
}
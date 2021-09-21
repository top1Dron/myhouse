import {add_form , deleteObject, getCookie } from '../../services.js'

$(document).ready(function(){
    // $('.slide').height('300px');
    $('.img-thumbnail').matchHeight();
    $('#add_more').click(function(e){
        add_form('id_blocks-TOTAL_FORMS', 'blocks', 'empty_form');
        $(`#id_blocks-${parseInt($(`#id_blocks-TOTAL_FORMS`).val()) - 1}-description`).summernote({
            height: '200px',
        });
        $('.img-thumbnail').matchHeight();
    });
    window.deleteBlock = deleteBlock;
    for(var i = 0; i < parseInt($(`#id_blocks-TOTAL_FORMS`).val());i++){
        $(`#id_blocks-${i}-description`).summernote({
            height: '200px',
        });
    }
    // id_blocks-0-description
})

function deleteBlock(button, form_ind){
    var url = $(button).attr('delete');
    
    if (url != null){
        $(button).parent().parent().addClass("d-none");
        $(`#id_blocks-${form_ind}-DELETE`).attr('checked', true);
    }
    else {
        $(button).parent().parent().remove();
    }
}
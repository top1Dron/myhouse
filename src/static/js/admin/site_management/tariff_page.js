import {add_form } from '../../services.js'

$(document).ready(function(){
    $(`#id_short_text`).summernote({
        height: '200px',
    });
    $('.img-thumbnail').matchHeight();
    $('#add_more').click(function(e){
        add_form('id_blocks-TOTAL_FORMS', 'blocks', 'empty_form');
        $('.img-thumbnail').matchHeight();
    });
    window.deleteBlock = deleteBlock;
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
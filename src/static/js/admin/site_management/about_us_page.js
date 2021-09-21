import {add_form, deleteObject, getCookie } from '../../services.js'


$(document).ready(function(){
    $('#id_short_text, #id_ai_short_text').summernote({
        height: '200px',
    });
    $('.gallery').matchHeight();
    $('.ad_gallery').matchHeight();

    window.getCookie = getCookie;
    window.deleteObject = deleteObject;
    window.deleteBlock = deleteBlock;

    $('#add_document').click(function(e){
        add_form('id_document_set-TOTAL_FORMS', 'documents', 'empty_form');
    });
})

function deleteBlock(button, form_ind){
    var url = $(button).attr('delete');
    
    if (url != null){
        $(button).parent().parent().addClass("d-none");
        $(`#id_document_set-${form_ind}-DELETE`).attr('checked', true);
    }
    else {
        $(button).parent().parent().remove();
    }
}
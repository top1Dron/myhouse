import { updateURLParameter, deleteObject, getCookie } from '../../services.js'

$(document).ready(function(){
    $('tr[data-href]').on("click", function() {
        document.location = $(this).data('href');
    });
    $('.delete-owner-button').click(function(e){
        deleteObject(this, getCookie('csrftoken'), 
            'Вы уверены, что хотите удалить данные этого пользователя из базы данных?',
            'Данные о пользователе удалены успешно!')
    });
})
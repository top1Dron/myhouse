import { deleteObject, getCookie } from '../../services.js'

$(document).ready(function(){
    $('tr[data-href]').click(function(e){
        document.location = $(this).data('href');
    });
    
    $('.delete-payment_type-button').click(function(e){
        deleteObject(this, getCookie('csrftoken'), 
            'Вы уверены, что хотите удалить данные этой статьи из базы данных?',
            'Данные статьи удалены успешно!')
    });
})
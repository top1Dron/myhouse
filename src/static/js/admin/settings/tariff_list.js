import { deleteObject, getCookie } from '../../services.js'

$(document).ready(function(){
    $('tr[data-href]').click(function(e){
        document.location = $(this).data('href');
    });
    
    $('.delete-tariff-button').click(function(e){
        deleteObject(this, getCookie('csrftoken'), 
            'Вы уверены, что хотите удалить данные этого тарифа из базы данных?',
            'Данные о тарифе удалены успешно!')
    });
})
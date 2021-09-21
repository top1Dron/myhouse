import { deleteObject, getCookie } from './services.js'

$(document).ready(function(){
    
    $('.delete-ticket-button').click(function(e){
        if(!$(this).hasClass('disabled')){
            deleteObject(this, getCookie('csrftoken'), 
                'Вы уверены, что хотите удалить выбранные данные?',
                'Данные удалены успешно!')
        }
    });
})
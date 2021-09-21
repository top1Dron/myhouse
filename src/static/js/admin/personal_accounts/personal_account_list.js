import { updateURLParameter, deleteObject, getCookie } from '../../services.js'

$(document).ready(function(){
    $('tr[data-href]').on("click", function() {
        document.location = $(this).data('href');
    });

    // $('#id_house_name_search_field').on('keydown', function(e){
    //     if (e.key == 'Enter'){
    //         document.location.href = updateURLParameter(
    //             window.location.search, 
    //             'name', 
    //             document.getElementById('id_house_name_search_field').value);
    //     }
    // });

    // $('#id_house_address_search_field').on('keydown', function(e){
    //     if (e.key == 'Enter'){
    //         document.location.href = updateURLParameter(
    //             window.location.search, 
    //             'address', 
    //             document.getElementById('id_house_address_search_field').value);
    //     }
    // });

    $('.delete-personal_account-button').click(function(e){
        deleteObject(this, getCookie('csrftoken'), 
            'Вы уверены, что хотите удалить данные этого лицевого счета из базы данных?',
            'Лицевой счёт удален успешно!')
    });
})
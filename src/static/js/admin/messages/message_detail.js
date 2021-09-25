import { deleteObject, getCookie, init_datatable } from '../../services.js'

$(document).ready(function(){
    $('#id_delete_message_button').click(function(e){
        deleteObject(this, getCookie('csrftoken'), 
            'Вы уверены, что хотите удалить это сообщение?',
            'Сообщение удалено!')
        Swal.fire({
            title: 'Вы уверены, что хотите удалить это сообщение?',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Да, удалить!',
            cancelButtonText: 'Нет, отменить!',
        }).then((result) => {
            if (result.isConfirmed) {
                var deleteUrl = $(this).attr("delete-url");
                var successUrl = $(this).attr('success-href');
                $.ajax({
                    url: deleteUrl,
                    type: 'DELETE',
                    data: {},
                    beforeSend: function (xhr) {
                        xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
                    },
                    success: function(resp){
                        Swal.fire(
                            'Сообщение удалено!',
                            'Удалено!',
                            'success'
                        )
                        document.location = successUrl;
                    }
                });
            }
        })
    })
})
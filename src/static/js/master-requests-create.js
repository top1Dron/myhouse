$(document).ready(function () {
    $('#convenientdate').datetimepicker({
        autoclose: true,
        locale: 'ru',
        format:'DD.MM.YYYY',
    });

    $('#convenienttime').datetimepicker({
        autoclose: true,
        locale: 'ru',
        format:'HH:mm',
    });
});
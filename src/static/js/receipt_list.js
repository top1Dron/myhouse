import { init_datatable } from './services.js'

$(document).ready(function(){

    $('tr[data-href]').on("click", function() {
        document.location = $(this).data('href');
    });

    init_datatable('id_receipts_table', [], [1], [2]);

    $('#id_receipts_table_filter').hide();
})
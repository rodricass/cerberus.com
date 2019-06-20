$(document).ready(function () {
    $(".documentos").change(function (event) {
        var cant = $(this)[0].files.length;
        $('#texto_archivos').html(cant + " archivos seleccionados");
        var fileName = $(this).val();
        var fileName = fileName.substring(12);
        $(".nombres").val(fileName);
    });
    $(".cancelar").click(function () {
        $('#file-form').trigger("reset");
    });
});

$('#modal-adjuntar').on('show.bs.modal', function (event) {
    console.log(event.relatedTarget);
    var button = $(event.relatedTarget);
    var recipient = button.data('whatever');
    console.log(recipient);
    $('#forma-adjuntar').attr('action', recipient);
});

$('#modalAdvice').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget);
    var recipient = button.data('urlprio');
    var recipient2 = button.data('urlsinprio');
    var recipient3 = button.data('caso');
    if (recipient3.length <= 40) {
        $('#caso_nombre').html(recipient3);
    }
    else {
        subnom = recipient3.substring(0, 35);
        $('#caso_nombre').html(subnom + "...");
        $('#caso_nombre').attr('title', recipient3);
    }
    $("#conPrivilegios").click(function () {
        $('#compartir_form').attr('action', recipient);
    });
    $("#sinPrivilegios").click(function () {
        $('#compartir_form').attr('action', recipient2);
    });
});




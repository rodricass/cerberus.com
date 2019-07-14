$('#modalAdvice').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget)
    var recipient = button.data('whatever')
    $('#enviar_form').attr('action', recipient)
})

$(document).ready(function () {
    $(".documentos").change(function () {
        var fileName = $(this).val();
        var fileName = fileName.substring(12);
        $(".nombres").val(fileName);
        var cant = $(this)[0].files.length;
        $('#texto_archivos').html(cant + " archivos seleccionados");
    });
    $(".cancelar").click(function () {
        $('#file-form').trigger("reset");
    })

});

$('#modalAdjuntar').on('show.bs.modal', function (event) {
    console.log(event.relatedTarget)
    var button = $(event.relatedTarget)
    var recipient = button.data('whatever')
    console.log(recipient)
    $('#forma-adjuntar').attr('action', recipient)
})

$('#modalEliminar').on('show.bs.modal', function (event) {
    console.log(event.relatedTarget)
    var button = $(event.relatedTarget)
    var recipient = button.data('whatever')
    console.log(recipient)
    $('#borrarForm').attr('action', recipient)
})

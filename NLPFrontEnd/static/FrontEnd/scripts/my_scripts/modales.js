$(".documentos").change(function () {
    var fileName = $(this).val();
    var cant = $(this)[0].files.length;
    $('#inside_text').html(cant + " archivo(s) seleccionado(s)");
    var fileNameAux = fileName.substring(12);
    $(".nombres").val(fileNameAux);
    $("#inside_text").css("top", "10rem");
    $("#inside_text").css("left", "18%");
});
$(".cancelar_modal_adjuntar").click(function () {
    $('#file-form').trigger("reset");
    $('#inside_text').html("&nbsp;&nbsp;&nbsp;Arrastre hasta aqu&#237; <br>o haga click (.docx,.txt)");
});
$(".aceptar_modal_adjuntar").click(function () {
    $(function () {
        $('#modal-adjuntar').modal('toggle');
        $('.container-fluid').css("opacity", "0.4");
        $('.container').css("opacity", "0.4");
        $('.contenedor').css("opacity", "0.4");
        $('#loading').show();
    });
});
$('#modal-adjuntar').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget);
    var recipient = button.data('whatever');
    var next = button.data('next');
    $('#forma-adjuntar').attr('action', recipient);
    $('#next').attr('value', next);
});
$('#modal-adjuntar').on('hidden.bs.modal', function (event) {
    $('#file-form').trigger("reset");
    $('#inside_text').html("&nbsp;&nbsp;&nbsp;Arrastre hasta aqu&#237; <br>o haga click (.docx,.txt)");
});

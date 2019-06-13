$("#seleccionar_casos").click(function () {
    $(".btn-adjuntar").animate({ right: '7.2rem' });
    $(".editar").animate({ left: '41.8rem' });
    $(".btn-nota").animate({ right: '-11.8rem' });
    $(".btn-compartir").animate({ right: '5.8rem' });
    $(".divisor-vertical").animate({ right: '6.2rem' });
    $(".botones_panel2").animate({ right: '-12rem' });
    $(".jumbocenter").animate({ marginLeft: '-4.5rem' });
    $(".checkboxes").show(500);
    $("#eliminar_caso").show();
    $("#finalizar_caso").show();
    $("#aclaracion").show();
    $("#crear_caso").hide();
    $("#seleccionar_casos").hide();
    $("#cancelar_seleccion").show();
}); 

$("#eliminar_caso").click(function () {
    $(".btn-adjuntar").animate({ right: '2.2rem' });
    $(".editar").animate({ left: '46.8rem' });
    $(".btn-nota").animate({ right: '-16.8rem' });
    $(".btn-compartir").animate({ right: '0.8rem' });
    $(".divisor-vertical").animate({ right: '1.2rem' });
    $(".botones_panel2").animate({ right: '-17rem' });
    $(".jumbocenter").animate({ marginLeft: '0.5rem' });
    $(".checkboxes").hide(250);
    $("#eliminar_caso").hide();
    $("#finalizar_caso").hide();
    $("#aclaracion").hide();
    $("#crear_caso").show();
    $("#seleccionar_casos").show();
    $("#cancelar_seleccion").hide();
});

$("#finalizar_caso").click(function () {
    $(".btn-adjuntar").animate({ right: '2.2rem' });
    $(".editar").animate({ left: '46.8rem' });
    $(".btn-nota").animate({ right: '-16.8rem' });
    $(".btn-compartir").animate({ right: '0.8rem' });
    $(".divisor-vertical").animate({ right: '1.2rem' });
    $(".botones_panel2").animate({ right: '-17rem' });
    $(".jumbocenter").animate({ marginLeft: '0.5rem' });
    $(".checkboxes").hide(250);
    $("#eliminar_caso").hide();
    $("#finalizar_caso").hide();
    $("#aclaracion").hide();
    $("#crear_caso").show();
    $("#seleccionar_casos").show();
    $("#cancelar_seleccion").hide();
});

$("#cancelar_seleccion").click(function () {
    $(".btn-adjuntar").animate({ right: '2.2rem' });
    $(".editar").animate({ left: '46.8rem' });
    $(".btn-nota").animate({ right: '-16.8rem' });
    $(".btn-compartir").animate({ right: '0.8rem' });
    $(".divisor-vertical").animate({ right: '1.2rem' });
    $(".botones_panel2").animate({ right: '-17rem' });
    $(".jumbocenter").animate({ marginLeft: '0.5rem' });
    $(".checkboxes").hide(250);
    $("#eliminar_caso").hide();
    $("#finalizar_caso").hide();
    $("#aclaracion").hide();
    $("#crear_caso").show();
    $("#seleccionar_casos").show();
    $("#cancelar_seleccion").hide();
    $(".checkboxes").prop('checked', false);
});

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
    })

});

$('#modal-adjuntar').on('show.bs.modal', function (event) {
    console.log(event.relatedTarget)
    var button = $(event.relatedTarget) 
    var recipient = button.data('whatever') 
    console.log(recipient)
    $('#forma-adjuntar').attr('action',recipient)
})

$('#modalAdvice').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget)
    var recipient = button.data('urlprio')
    var recipient2 = button.data('urlsinprio')
    var recipient3 = button.data('caso')
    if (recipient3.length <= 40) {
        $('#caso_nombre').html(recipient3)
    }
    else {
        subnom = recipient3.substring(0, 35)
        $('#caso_nombre').html(subnom + "...")
        $('#caso_nombre').attr('title', recipient3)
    }
    $("#conPrivilegios").click(function () {
        $('#compartir_form').attr('action', recipient)
    })
    $("#sinPrivilegios").click(function () {
        $('#compartir_form').attr('action', recipient2)
    })
})




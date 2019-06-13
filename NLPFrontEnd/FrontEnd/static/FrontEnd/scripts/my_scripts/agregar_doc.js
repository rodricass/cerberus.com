$(document).ready(function () {
    $("#id_documento").change(function () {
        var fileName = $(this).val();
        var fileName = fileName.substring(12);
        $("#id_nombre_doc").val(fileName);
    });
    $("#cancelar").click(function () {
        $('#file-form').trigger("reset");
    })

});


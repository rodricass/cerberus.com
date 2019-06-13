from django.contrib import admin
from FrontEnd.models import *
from simple_history.admin import SimpleHistoryAdmin

class CasoAdmin(SimpleHistoryAdmin):
    list_display = ('nombre', 'propietario', 'fecha_agregado', 'modelo', 'eliminado', 'finalizado_correcto', 'finalizado_incorrecto')
    list_filter = ('propietario', 'eliminado', 'fecha_agregado', 'modelo', 'usuario', 'finalizado_correcto', 'finalizado_incorrecto')

class DocumentoAdmin(SimpleHistoryAdmin):
    list_display = ('titulo','propietario_doc','eliminado','fecha_agregado')
    list_filter = ('propietario_doc','fecha_agregado','caso','eliminado')

class ParrafoAdmin(SimpleHistoryAdmin):
    list_display = ('parrafo','nro','doc','eliminado')
    list_filter = ('eliminado','doc')

class EntidadesDocAdmin(SimpleHistoryAdmin):
    list_display = ('string', 'tipo', 'start', 'end', 'eliminado')
    list_filter = ('tipo', 'eliminado')

class TokensDocAdmin(SimpleHistoryAdmin):
    list_display = ('aparicion', 'tipo', 'lema', 'categoria', 'eliminado')
    list_filter = ('tipo', 'categoria', 'eliminado')

class MensajeAdmin(SimpleHistoryAdmin):
    list_display = ('mensaje','emisor', 'receptor', 'fecha_agregado', 'caso', 'eliminado')
    list_filter = ('emisor', 'receptor', 'fecha_agregado', 'caso', 'eliminado')

class NotaAdmin(SimpleHistoryAdmin):
    list_display = ('nota','fecha_agregado','eliminado')
    list_filter = ('nota','fecha_agregado','eliminado')

class ResultadoHeaderAdmin(SimpleHistoryAdmin):
    list_display = ('fecha','busqueda','caso','tipo','estado','eliminado')
    list_filter = ('fecha','busqueda','caso','estado','eliminado')

class InformeAdmin(SimpleHistoryAdmin):
    list_display = ('fecha','busqueda','caso','propietario','eliminado')
    list_filter = ('fecha','busqueda','caso','propietario','eliminado')

admin.site.register(EntidadesDoc, EntidadesDocAdmin)
admin.site.register(Caso, CasoAdmin)
admin.site.register(TokensDoc, TokensDocAdmin)
admin.site.register(Mensaje, MensajeAdmin)
admin.site.register(Documento, DocumentoAdmin)
admin.site.register(Parrafo, ParrafoAdmin)
admin.site.register(Nota, NotaAdmin)
admin.site.register(ResultadoHeader, ResultadoHeaderAdmin)
admin.site.register(Informe, InformeAdmin)

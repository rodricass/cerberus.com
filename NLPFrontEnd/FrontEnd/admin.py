from django.contrib import admin
from FrontEnd.models import *
from simple_history.admin import SimpleHistoryAdmin

admin.site.site_header = 'Cerberus administration'

class InvestigacionAdmin(SimpleHistoryAdmin):
    list_display = ('nombre', 'propietario', 'fecha_agregado', 'modelo', 'eliminado', 'finalizado_correcto', 'finalizado_incorrecto')
    list_filter = ('propietario', 'eliminado', 'fecha_agregado', 'modelo', 'usuario', 'finalizado_correcto', 'finalizado_incorrecto')

class DocumentoAdmin(SimpleHistoryAdmin):
    list_display = ('nombre_doc','propietario_doc','eliminado','fecha_agregado')
    list_filter = ('propietario_doc','fecha_agregado','investigacion','eliminado')

class ParrafoAdmin(SimpleHistoryAdmin):
    list_display = ('parrafo','nro','doc','eliminado')
    list_filter = ('eliminado','doc')

class EntidadesDocAdmin(SimpleHistoryAdmin):
    list_display = ('string', 'tipo', 'start', 'end', 'incorrecta', 'eliminado')
    list_filter = ('tipo', 'incorrecta','eliminado')

class TokensDocAdmin(SimpleHistoryAdmin):
    list_display = ('aparicion', 'tipo', 'lema', 'categoria', 'eliminado')
    list_filter = ('tipo', 'categoria', 'eliminado')

class MensajeAdmin(SimpleHistoryAdmin):
    list_display = ('mensaje','emisor', 'receptor', 'fecha_agregado', 'investigacion', 'eliminado')
    list_filter = ('emisor', 'receptor', 'fecha_agregado', 'investigacion', 'eliminado')

class NotaAdmin(SimpleHistoryAdmin):
    list_display = ('nota','fecha_agregado','eliminado')
    list_filter = ('nota','fecha_agregado','eliminado')

class ResultadoHeaderAdmin(SimpleHistoryAdmin):
    list_display = ('fecha','busqueda','investigacion','tipo','estado','eliminado')
    list_filter = ('fecha','busqueda','investigacion','estado','eliminado')

class InformeAdmin(SimpleHistoryAdmin):
    list_display = ('fecha','busqueda','investigacion','propietario','eliminado')
    list_filter = ('fecha','busqueda','investigacion','propietario','eliminado')

class RegexAdmin(SimpleHistoryAdmin):
    list_display = ('nombre','patron','orden','eliminado')
    list_filter = ('nombre','patron','orden','eliminado')

admin.site.register(EntidadesDoc, EntidadesDocAdmin)
admin.site.register(Investigacion, InvestigacionAdmin)
admin.site.register(TokensDoc, TokensDocAdmin)
admin.site.register(Mensaje, MensajeAdmin)
admin.site.register(Documento, DocumentoAdmin)
admin.site.register(Parrafo, ParrafoAdmin)
admin.site.register(Nota, NotaAdmin)
admin.site.register(ResultadoHeader, ResultadoHeaderAdmin)
admin.site.register(Informe, InformeAdmin)
admin.site.register(Regex, RegexAdmin)

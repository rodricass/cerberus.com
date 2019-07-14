"""
Definition of urls for NLPFrontEnd.
"""

from datetime import datetime
from django.conf.urls import url
import django.contrib.auth.views
from django.conf import settings
from django.conf.urls.static import static

import FrontEnd.forms
import FrontEnd.views as views

# Uncomment the next lines to enable the admin:
from django.conf.urls import include
from django.contrib import admin
from django.conf import settings
from django.http import HttpResponseRedirect


admin.autodiscover()

urlpatterns = [    
    url(r'^favicon.ico/$', lambda x: HttpResponseRedirect(settings.STATIC_URL+'FrontEnd/images/wCancerbero.png')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    #Investigacion
    url(r'^investigaciones/en_curso/(?P<investigacion_id>\d+)/$', views.investigacion, name='investigacion'),

    #Investigaciones en curso
    url(r'^investigaciones/buscador_inteligente/editar_entidad/(?P<tipo>[A-z úé]+)/(?P<id_ent>\d+)/(?P<id_investigacion>\d+)/(?P<camino>.+)/$', views.editar_entidad, name='editar_entidad'),
    url(r'^investigaciones/buscador_inteligente/guardar_resultadoInteligente/(?P<tipo>[A-z úé]+)/(?P<investigacion_id>\d+)/(?P<camino>.+)/$', views.guardar_resultadoInteligente, name='guardar_resultadoInteligente'),
    url(r'^investigaciones/buscador_guiado/guardar_resultadoGuiado/(?P<tipo>.+)/(?P<investigacion_id>\d+)/(?P<camino>.+)/$', views.guardar_resultadoGuiado, name='guardar_resultadoGuiado'),
    url(r'^investigaciones/buscado_general/guardar_resultadoGeneral/(?P<investigacion_id>\d+)/(?P<expresion>.+)/(?P<camino>.+)/$', views.guardar_resultadoGeneral, name='guardar_resultadoGeneral'),
    url(r'^investigaciones/buscador_inteligente/(?P<tipo>[A-z óúé]+)/(?P<investigacion_id>\d+)/(?P<camino>.+)/$', views.buscador_inteligente, name='buscador_inteligente'),
    url(r'^investigaciones/buscador_guiado/(?P<tipo>.+)/(?P<id_regex>\d+)/(?P<investigacion_id>\d+)/(?P<camino>.+)/$', views.buscador_guiado, name='buscador_guiado'),
    url(r'^investigaciones/eliminar_regex/(?P<tipo>.+)/(?P<id_regex>\d+)/(?P<investigacion_id>\d+)/(?P<camino>.+)/$', views.eliminar_regex, name='eliminar_regex'),
    url(r'^investigaciones/compartir_investigaciones/(?P<investigacion_id>\d+)/(?P<tipo>[A-z úé]+)/$', views.compartir_investigaciones, name='compartir_investigaciones'),
    url(r'^investigaciones/administrar_investigaciones/(?P<tipo>[A-z úé]+)/$', views.administrar_investigaciones, name='administrar_investigaciones'),
    url(r'^investigaciones/buscador_general/(?P<investigacion_id>\d+)/(?P<camino>.+)/$', views.buscador_general, name='buscador_general'),
    url(r'^investigaciones/agregar_doc/(?P<investigacion_id>\d+)/$', views.agregar_doc, name='agregar_doc'),
    url(r'^investigaciones/editar_investigacion/(?P<investigacion_id>\d+)/(?P<camino>.+)$', views.editar_investigacion, name='editar_investigacion'),
    url(r'^investigaciones/nueva_investigacion/(?P<camino>.+)/$', views.nueva_investigacion, name='nueva_investigacion'),
    url(r'^investigaciones/en_curso/$', views.investigaciones, name='investigaciones'),

    #Resultados
    url(r'^resultados/eliminar_resultadoInvestigacion/(?P<investigacion_id>\d+)/(?P<resultado_id>\d+)/(?P<tipo>[A-z úé]+)/(?P<camino>.+)/$', views.eliminar_resultadoInvestigacion, name='eliminar_resultadoInvestigacion'),
    url(r'^resultados/eliminar_resultado/(?P<investigacion_id>\d+)/(?P<resultado_id>\d+)/(?P<tipo>[A-z úé]+)/(?P<camino>.+)/$', views.eliminar_resultado, name='eliminar_resultado'),
    url(r'^resultados/crearInforme/(?P<resultado_id>\d+)/(?P<tipo_informe>[A-z úé]+)/(?P<camino>.+)/$', views.crearInforme, name='crearInforme'),
    url(r'^resultados/ver_resultado/(?P<resultado_id>\d+)/(?P<tipo>[A-z úé]+)/(?P<camino>.+)/$', views.ver_resultado, name='ver_resultado'),
    url(r'^resultados/$', views.resultados, name='resultados'),

    #Investigaciones finalizadas
    url(r'^investigaciones/documentos_investigacion/(?P<investigacion_id>\d+)/(?P<destino>FrontEnd/documentos_[a-z]+\.html)/(?P<camino>.+)/$', views.documentos_investigacion, name='documentos_investigacion'),
    url(r'^investigaciones/resultados_investigacion/(?P<investigacion_id>\d+)/(?P<destino>FrontEnd/resultados_[a-z]+\.html)/(?P<camino>.+)/$', views.resultados_investigacion, name='resultados_investigacion'),
    url(r'^investigaciones/informes_investigacion/(?P<investigacion_id>\d+)/(?P<destino>FrontEnd/informes_[a-z]+\.html)/(?P<camino>.+)/$', views.informes_investigacion, name='informes_investigacion'),
    url(r'^investigaciones/finalizadas/compartir_investigacionFinalizada/(?P<investigacion_id>\d+)/$', views.compartir_investigacionFinalizada, name='compartir_investigacionFinalizada'),
    url(r'^investigaciones/finalizadas/eliminar_finalizada/(?P<investigacion_id>\d+)/$', views.eliminar_finalizada, name='eliminar_finalizada'),
    url(r'^investigaciones/finalizadas/$', views.investigaciones_finalizadas, name='investigaciones_finalizadas'),
    url(r'^investigaciones/finalizadas/(?P<investigacion_id>\d+)/$', views.investigacion_finalizada, name='investigacion_finalizada'),

    #Documentos
    url(r'^documentos/mensaje_nuevo/(?P<id_doc>\d+)/(?P<id_investigacion>\d+)/(?P<camino>.+)/$', views.mensaje_nuevo, name='mensaje_nuevo'),
    url(r'^documentos/eliminar_doc/(?P<id_doc>\d+)/(?P<id_investigacion>\d+)/$', views.eliminar_doc, name='eliminar_doc'),
    url(r'^documentos/eliminar_doc_investigacion/(?P<id_doc>\d+)/(?P<id_investigacion>\d+)/(?P<camino>.+)/$', views.eliminar_doc_investigacion, name='eliminar_doc_investigacion'),
    url(r'^documentos/agregar_docDocumentos/(?P<investigacion_id>\d+)/$', views.agregar_docDocumentos, name='agregar_docDocumentos'),
    url(r'^documentos/agregar_docInvestigacion/(?P<investigacion_id>\d+)/(?P<camino>.+)/$', views.agregar_docInvestigacion, name='agregar_docInvestigacion'),
    url(r'^documentos/ver_doc/(?P<id_doc>\d+)/$', views.ver_doc, name='ver_doc'),
    url(r'^documentos/$', views.documentos, name='documentos'),

    #Notas
    url(r'^notas/eliminar_nota/(?P<id>\d+)/(?P<tipo>[A-z úé]+)/(?P<id_nota>\d+)/(?P<camino>.+)/$', views.eliminar_nota, name='eliminar_nota'),
    url(r'^ver_notas/eliminar_notainvestigacion/(?P<id_investigacion>\d+)/(?P<id_nota>\d+)/$', views.eliminar_notainvestigacion, name='eliminar_notainvestigacion'),
    url(r'^notas/(?P<id>\d+)/(?P<tipo>[A-z úé]+)/(?P<camino>.+)/$', views.notas, name='notas'),
    url(r'^ver_notas/crear_nota/(?P<id_investigacion>\d+)/$', views.crear_nota, name='crear_nota'),
    url(r'^ver_notas_especifica/(?P<investigacion_id>\d+)/$', views.ver_notas_especifica, name='ver_notas_especifica'),
    url(r'^ver_notas/$', views.ver_notas, name='ver_notas'),

    #Informes
    url(r'^informes/eliminar_informe/(?P<informe_id>\d+)/$', views.eliminar_informe, name='eliminar_informe'),
    url(r'^informes/ver_informe/(?P<id_informe>\d+)/$', views.ver_informe, name='ver_informe'),
    url(r'^informes/$', views.informes, name='informes'),

    url(r'^login/$',
        django.contrib.auth.views.login,
        {
            'redirect_authenticated_user': True,
            'template_name': 'FrontEnd/login.html',
            'authentication_form': FrontEnd.forms.BootstrapAuthenticationForm,
            'extra_context':
            {
                'title': 'Cerberus',
                'year': datetime.now().year,
            }
        },
        name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    # Home
    url(r'^eliminar_docInicio/(?P<id_doc>\d+)/$', views.eliminar_docInicio, name='eliminar_docInicio'),
    url(r'^eliminar_mensaje/(?P<id_msj>\d+)/$', views.eliminar_mensaje, name='eliminar_mensaje'),
    url(r'^$', views.home, name='home'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
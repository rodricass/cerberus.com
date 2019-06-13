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
admin.autodiscover()

urlpatterns = [    

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    #Casos en curso
    url(r'^casos/en_curso/buscador_inteligente/editar_entidad/(?P<tipo>[A-z úé]+)/(?P<id_ent>\d+)/(?P<id_caso>\d+)/$', views.editar_entidad, name='editar_entidad'),
    url(r'^casos/en_curso/buscador_inteligente/guardar_resultadoInteligente/(?P<tipo>[A-z úé]+)/(?P<caso_id>\d+)/$', views.guardar_resultadoInteligente, name='guardar_resultadoInteligente'),
    url(r'^casos/en_curso/buscador_guiado/guardar_resultadoGuiado/(?P<tipo>[A-z úé]+)/(?P<caso_id>\d+)/$', views.guardar_resultadoGuiado, name='guardar_resultadoGuiado'),
    url(r'^casos/en_curso/buscado_general/guardar_resultadoGeneral/(?P<caso_id>\d+)/(?P<expresion>.+)/$', views.guardar_resultadoGeneral, name='guardar_resultadoGeneral'),
    url(r'^casos/en_curso/buscador_inteligente/(?P<tipo>[A-z óúé]+)/(?P<caso_id>\d+)/$', views.buscador_inteligente, name='buscador_inteligente'),
    url(r'^casos/en_curso/buscador_guiado/(?P<tipo>[A-z úé]+)/(?P<caso_id>\d+)/$', views.buscador_guiado, name='buscador_guiado'),
    url(r'casos/en_curso/compartir_casos/(?P<caso_id>\d+)/(?P<tipo>[A-z úé]+)/$', views.compartir_casos, name='compartir_casos'),
    url(r'^casos/en_curso/administrar_casos/(?P<tipo>[A-z úé]+)/$', views.administrar_casos, name='administrar_casos'),
    url(r'^casos/en_curso/buscador_general/(?P<caso_id>\d+)/$', views.buscador_general, name='buscador_general'),
    url(r'^casos/en_curso/agregar_doc/(?P<caso_id>\d+)/$', views.agregar_doc, name='agregar_doc'),
    url(r'^casos/en_curso/editar_caso/(?P<caso_id>\d+)/$', views.editar_caso, name='editar_caso'),
    url(r'^casos/en_curso/nuevo_caso/$', views.nuevo_caso, name='nuevo_caso'),
    url(r'^casos/en_curso/$', views.casos, name='casos'),

    #Resultados
    url(r'^resultados/eliminar_resultadoCaso/(?P<caso_id>\d+)/(?P<resultado_id>\d+)/(?P<tipo>[A-z úé]+)/$', views.eliminar_resultadoCaso, name='eliminar_resultadoCaso'),
    url(r'^resultados/eliminar_resultado/(?P<caso_id>\d+)/(?P<resultado_id>\d+)/(?P<tipo>[A-z úé]+)/$', views.eliminar_resultado, name='eliminar_resultado'),
    url(r'^resultados/crearInforme/(?P<resultado_id>\d+)/(?P<tipo_informe>[A-z úé]+)/$', views.crearInforme, name='crearInforme'),
    url(r'^resultados/ver_resultado/(?P<resultado_id>\d+)/(?P<tipo>[A-z úé]+)/$', views.ver_resultado, name='ver_resultado'),
    url(r'^resultados/$', views.resultados, name='resultados'),

    #Casos finalizados
    url(r'^casos/documentos_caso/(?P<caso_id>\d+)/(?P<destino>FrontEnd/documentos_[a-z]+\.html)/$', views.documentos_caso, name='documentos_caso'),
    url(r'^casos/resultados_caso/(?P<caso_id>\d+)/(?P<destino>FrontEnd/resultados_[a-z]+\.html)/$', views.resultados_caso, name='resultados_caso'),
    url(r'^casos/informes_caso/(?P<caso_id>\d+)/(?P<destino>FrontEnd/informes_[a-z]+\.html)/$', views.informes_caso, name='informes_caso'),
    url(r'casos/finalizados/compartir_casosFinalizado/(?P<caso_id>\d+)/$', views.compartir_casoFinalizado, name='compartir_casoFinalizado'),
    url(r'^casos/finalizados/eliminar_finalizado/(?P<caso_id>\d+)/$', views.eliminar_finalizado, name='eliminar_finalizado'),
    url(r'^casos/finalizados/$', views.casos_finalizados, name='casos_finalizados'),

    #Documentos
    url(r'^documentos/mensaje_nuevo/(?P<id_doc>\d+)/(?P<id_caso>\d+)/$', views.mensaje_nuevo, name='mensaje_nuevo'),
    url(r'^documentos/eliminar_doc/(?P<id_doc>\d+)/(?P<id_caso>\d+)/$', views.eliminar_doc, name='eliminar_doc'),
    url(r'^documentos/agregar_docDocumentos/(?P<caso_id>\d+)/$', views.agregar_docDocumentos, name='agregar_docDocumentos'),
    url(r'^documentos/agregar_docCaso/(?P<caso_id>\d+)/$', views.agregar_docCaso, name='agregar_docCaso'),
    url(r'^documentos/ver_doc/(?P<id_doc>\d+)/$', views.ver_doc, name='ver_doc'),
    url(r'^documentos/$', views.documentos, name='documentos'),

    #Notas
    url(r'^notas/eliminar_nota/(?P<id>\d+)/(?P<tipo>[A-z úé]+)/(?P<id_nota>\d+)/$', views.eliminar_nota, name='eliminar_nota'),
    url(r'^ver_notas/eliminar_notacaso/(?P<id_caso>\d+)/(?P<id_nota>\d+)/$', views.eliminar_notacaso, name='eliminar_notacaso'),
    url(r'^notas/(?P<id>\d+)/(?P<tipo>[A-z úé]+)/$', views.notas, name='notas'),
    url(r'^ver_notas/crear_nota/(?P<id_caso>\d+)/$', views.crear_nota, name='crear_nota'),
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
    url(r'^eliminar_usuario/$', views.eliminar_usuario, name='eliminar_usuario'),
    url(r'^crear_usuario/$', views.crear_usuario, name='crear_usuario'),
    url(r'^$', views.home, name='home'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
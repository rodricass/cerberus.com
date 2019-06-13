"""
Definition of views.
"""

from django.shortcuts import render
from django.http import HttpRequest
from django.http import Http404
from django.template import RequestContext
from datetime import datetime
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User
import os
import posixpath
import re
import hashlib
import json
import time
from django.utils.safestring import SafeString
from docx import Document
from docx.shared import Pt
from django.db.models import Q
from django.views.generic.edit import FormView

from .models import *
from .forms import CasoForm, DocumentoForm, CasoFormEdit, BuscadorGeneralForm, BuscadorCasosForm, NotaForm, UsuariosForm, UsuarioNuevoForm
from .functions import *

from .myclasses import *
from collections import defaultdict
from .genericos import *

#***********************************************************************************************************************************************************************
#********************************************************************************** START INICIO ***********************************************************************
#***********************************************************************************************************************************************************************

@login_required
def home(request):
    """Crea la página de inicio"""
    assert isinstance(request, HttpRequest)
    mensajes = Mensaje.objects.filter(eliminado=False).filter(receptor=request.user).order_by('-fecha_agregado')
    casos = Caso.objects.filter(usuario=request.user).filter(eliminado=False).filter(finalizado_incorrecto=False).filter(finalizado_correcto=False).order_by('-fecha_agregado')[:2]
    documentos = Documento.objects.filter(usuario=request.user).filter(eliminado=False).order_by('-fecha_agregado')[:7]
    form = DocumentoForm()
    form_usuario = UsuariosForm(request.user)
    context = {
            'title':'Home',
            'year':datetime.now().year,
            'mensajes':mensajes,
            'casos':casos,
            'formDoc':form,
            'form_usuario':form_usuario,
            'documentos':documentos,
            }
    if request.user.is_superuser:
        form_crear = UsuarioNuevoForm()
        form_usuario = UsuariosForm(request.user)
        context['form_crear'] = form_crear
        context['form_usuario'] = form_usuario
    return render(request,'FrontEnd/index.html',context)

def crear_usuario(request):
    """Crea usuario nuevo"""
    if request.method == 'POST':
        form = UsuarioNuevoForm(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            contraseña = form.cleaned_data['contraseña']
            user = User.objects.create_user(nombre, '', contraseña)
            user.save()

    return HttpResponseRedirect(reverse('home'))

def eliminar_usuario(request):
    """Elimina usuario existente"""
    if request.method == 'POST':
        usuario = request.POST.get('usuarios')
        usuario_instance = User.objects.get(id=usuario)
        usuario_instance.delete()

    return HttpResponseRedirect(reverse('home'))

def logout_view(request):
    """Cierra sesión de usuario"""
    logout(request)
    return HttpResponseRedirect(reverse('home'))

#***********************************************************************************************************************************************************************
#********************************************************************************** END INICIO *******************************************************************
#***********************************************************************************************************************************************************************


#***********************************************************************************************************************************************************************
#********************************************************************************** START DOCUMENTOS *******************************************************************
#***********************************************************************************************************************************************************************

@login_required
def documentos(request):
    """Genera la vista de todos los documentos subidos por el usuario"""
    form = BuscadorCasosForm(request.user)
    formDoc = DocumentoForm()
    context = {'form':form, 
               'formDoc':formDoc,
               'title':'Documentos'
               }
    if request.method == 'POST':
        id_caso = request.POST.get('casos')
        caso = Caso.objects.get(id=id_caso)
        documentos = caso.documento_set.filter(eliminado=False).order_by('-fecha_agregado')
        context['id_caso'] = id_caso
        context['documentos'] = documentos
        context['inicial'] = False
    return render(request,'FrontEnd/documentos.html',context)

@login_required
def documentos_caso(request,caso_id,destino):
    """Genera la vista de todos los documentos subidos por el usuario para un caso """
    formDoc = DocumentoForm()
    context = {
                'formDoc':formDoc,
                'title':'Documentos de caso'
               }
    caso = Caso.objects.get(id=caso_id)
    documentos = caso.documento_set.filter(eliminado=False).order_by('-fecha_agregado')
    context['id_caso'] = caso_id
    context['documentos'] = documentos
    return render(request,destino,context)

def crear_documento_general(request,file,form,caso_id):
    """Crea y guarda documento en base a forma"""
    
    #Crea los hashs en base al contenido del documento
    hash_md5 = hashlib.md5()
    hash_sha = hashlib.sha1()
    for c in file.chunks():
        hash_md5.update(c)
        hash_sha.update(c)

    hash_md5 = hash_md5.hexdigest()
    hash_sha1 = hash_sha.hexdigest()
    propietario_doc = request.user

    #Parsea el documento en base a si es txt o docx
    nombre, punto, ext = file.name.rpartition(".")
    ext = ext.lower()
    
    lector = ExtensionArchivo().getLector(ext,file)
    texto = lector.read()

    nuevo_doc = Documento(titulo=file.name,nombre_doc=file.name,documento=file,texto=texto,propietario_doc=propietario_doc,hash_md5=hash_md5,hash_sha1=hash_sha1,eliminado=False)
    nuevo_doc.save()

    #Divide al documento en párrafos para mejor procesamiento
    dividirParrafos(nuevo_doc)

    #Crea las entidades correspondientes a los párrafos del documento
    crearEntidades(nuevo_doc,caso_id)

    #Relaciona el documento con el usuario que lo está utilizando y con el caso correspondiente
    nuevo_doc.usuario.add(request.user)
    nuevo_doc.caso.add(caso_id)

    nuevo_doc.save()

@login_required
def agregar_doc(request, caso_id):
    """ Crear un documento en base a un archivo cargado en el sistema por el usuario"""
    
    if request.method == 'POST':
        #Crea el objeto documento que solo contiene la ubicación del documento en el servidor
        next = request.POST.get('next', '/')
        form = DocumentoForm(request.POST, request.FILES)
        files = request.FILES.getlist('documento')
        if form.is_valid():
            for f in files:
                crear_documento_general(request,f,form,caso_id)
                
    return HttpResponseRedirect(reverse(next))

#class FileFieldView(FormView):
#    form_class = DocumentoForm
#    success_url = ''

#    def post(self,request,*args,**kwargs):
#        form_class = self.get_form_class()
#        form = self.get_form(form_class)
#        next = request.POST.get('next', '/')
#        self.success_url = reverse_lazy(next)
#        caso_id = self.kwargs['caso_id']

#        if form.is_valid():
#            crear_documento_general(request,form,caso_id)
#            return self.form_valid(form)
#        else:
#            return self.form_invalid(form)

@login_required
def agregar_docDocumentos(request, caso_id):
    """Crear documento desde la pantalla de documentos en base a un archivo cargado en el sistema por el usuario"""
    
    #Crea el objeto documento que solo contiene la ubicación del documento en el servidor
    form = DocumentoForm(request.POST, request.FILES)
    if form.is_valid():
        crear_documento_general(request,form,caso_id)

    form = BuscadorCasosForm(request.user)
    formDoc = DocumentoForm()
    context = {'form':form, 'formDoc':formDoc }
    caso = Caso.objects.get(id=caso_id)
    documentos = caso.documento_set.filter(eliminado=False).order_by('-fecha_agregado')
    context['id_caso'] = caso_id
    context['documentos'] = documentos
    context['inicial'] = False
    return render(request,'FrontEnd/documentos.html',context)

@login_required
def agregar_docCaso(request,caso_id):
    """Crear documento desde la pantalla de documentos de caso en base a un archivo cargado en el sistema por el usuario"""
    form = DocumentoForm(request.POST, request.FILES)
    if form.is_valid():
        crear_documento_general(request,form,caso_id)

    destino = 'FrontEnd/documentos_caso.html'

    return HttpResponseRedirect(reverse('documentos_caso',args=[caso_id,destino]))

def crearEntidades(documento,caso_id):
    """Crea las entidades en base al análisis nlp de un documento"""
    caso = Caso.objects.get(id=caso_id)
    modelo = model_factory(caso.modelo)
    rx = re.compile("\s+")
    parrafos = Parrafo.objects.filter(doc_id=documento)
    resultado_tokenizer = []
    resultado_ner = []
    for parrafo in parrafos:
        entidades = []
        texto = rx.sub(" ", parrafo.parrafo)
        task_id = modelo.analyze(texto)
        while not modelo.is_analysis_ready(task_id):
            time.sleep(0.1)
        results = modelo.get_task_results(task_id)
        tokens = results['tokenizer_results']
        for token in [token.to_dict() for token in tokens]:
            resultado_tokenizer.append([token['base_form'],token['part_of_speech'],token['sentence'],token['token_text'],token['analysis_result']['category_detected'],parrafo.id])
        entidades = results['ner_results']
        for entidad in [entidad.to_dict() for entidad in entidades]:
            resultado_ner.append([entidad['text'],entidad['start_pos'],entidad['end_pos'],entidad['label'],parrafo.id])

        #doc = nlp(texto)
        #entidades.extend(doc.ents)
        #for e in entidades:
        #    ent_aux = EntidadesDoc(doc=documento, tipo=e.label_, string=e.string, string_original=e.string, start=e.start_char, end=e.end_char, parrafo_id=parrafo.id, eliminado=False)
        #    ent_aux.save()

    for entidad in resultado_ner:
        parrafo = Parrafo.objects.get(id=entidad[4])
        ent_aux = EntidadesDoc(doc=documento, tipo=entidad[3], string=entidad[0], string_original=entidad[0], start=entidad[1], end=entidad[2], parrafo=parrafo, eliminado=False)
        ent_aux.save()

    for token in resultado_tokenizer:
        parrafo = Parrafo.objects.get(id=token[5])
        token_aux = TokensDoc(doc=documento, aparicion=token[3], tipo=GetTipoToken().getTipoToken(token[1]), frase=token[2], lema=token[0], categoria=token[4], parrafo=parrafo, eliminado=False)
        token_aux.save()

def  dividirParrafos(documento):
    """Segmenta el texto de un documento para ser almacenado por párrafos"""
    texto = documento.texto
    parrafos = texto.split("\n\n")
    i = 1
    for p in parrafos:
        parrafo = Parrafo(nro=i, doc_id=documento.id, parrafo=p, eliminado=False)
        parrafo.save()
        i = i + 1

def eliminar_documentos_general(id_doc):
    """Eliminar documentos"""
    doc = Documento.objects.get(id=id_doc)
    doc.eliminado = True
    doc.save()
    parrafos = Parrafo.objects.filter(doc=doc)
    for parrafo in parrafos:
        parrafo.eliminado = True
        parrafo.save()
    entidades = EntidadesDoc.objects.filter(doc=doc)
    for entidad in entidades:
        entidad.eliminado = True
        entidad.save()
    tokens = TokensDoc.objects.get(doc=doc)
    for token in tokens:
        token.eliminado = True
        token.save()
    notas = NotaDocumento.objects.filter(entidad=doc)
    for nota in notas:
        nota.eliminado = True
        nota.save()
    mensajes = Mensaje.objects.filter(documento=doc)
    for mensaje in mensajes:
        mensaje.eliminado = True
        mensaje.save()

@login_required
def eliminar_doc(request, id_doc, id_caso):
    """Eliminar un documento del caso"""
    next = ''
    if request.method == 'POST':
        next = request.POST.get('next', '/')
        eliminar_documentos_general(id_doc)
    caso = Caso.objects.get(id=id_caso)
    documentos = caso.documento_set.filter(eliminado=False).order_by('-fecha_agregado')
    form = BuscadorCasosForm(request.user)
    formDoc = DocumentoForm()
    context = {'form':form,
               'formDoc':formDoc,
               'documentos':documentos,
               'inicial':False,
               'id_caso':id_caso}
    return render(request,next,context)


def eliminar_docInicio(request,id_doc):
    """Elimina un documento desde la pantalla de inicio"""

    eliminar_documentos_general(id_doc)
    
    return HttpResponseRedirect(reverse('home'))

@login_required
def ver_doc(request, id_doc):
    """Descarga el documento para que el usuario pueda leerlo desde su dispositivo"""
    
    doc = Documento.objects.get(id=id_doc)
    nombre, punto, ext = str(doc.documento).rpartition(".")

    content = ExtensionArchivo().getResponseDoc(ext)

    response = HttpResponse(doc.documento, content_type=content)
    file_path = f'{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/documentos{doc.documento}'
    response['Content-Disposition'] = 'attachment; filename=%s' % doc.titulo

    return response

@login_required
def mensaje_nuevo(request, id_doc, id_caso):
    """Genera una solicitud de eliminación para el propietario del documento"""
    form = BuscadorCasosForm(request.user)
    formDoc = DocumentoForm()
    context = {'form':form,
               'formDoc': formDoc,}
    if request.method == 'POST':
        next = request.POST.get('next', '/')
        msj = request.POST.get('mensaje')
        doc = Documento.objects.get(id = id_doc)
        caso = Caso.objects.get(id=id_caso)
        mensaje = Mensaje()
        mensaje.emisor = request.user
        mensaje.receptor = doc.propietario_doc
        mensaje.mensaje = msj
        mensaje.documento = doc
        mensaje.eliminado = False
        mensaje.caso = caso
        mensaje.save()
        documentos = caso.documento_set.filter(eliminado=False).order_by('-fecha_agregado')
        context['documentos'] = documentos
        context['inicial'] = False
        context['id_caso'] = id_caso
    return render(request,next,context)

@login_required
def eliminar_mensaje(request,id_msj):
    """Elimina un mensaje de solicitud de eliminación de documento"""
    mensaje = Mensaje.objects.get(id=id_msj)
    mensaje.eliminado = True
    mensaje.save()
    
    return HttpResponseRedirect(reverse('home'))



#***********************************************************************************************************************************************************************
#********************************************************************************** END DOCUMENTOS *******************************************************************
#***********************************************************************************************************************************************************************

#***********************************************************************************************************************************************************************
#****************************************************************************************** START CASOS ****************************************************************
#***********************************************************************************************************************************************************************

@login_required
def casos(request):
    """Genera la vista de los casos de un usuario determinado"""
    
    casos = Caso.objects.filter(usuario=request.user).filter(eliminado=False).filter(finalizado_incorrecto=False).filter(finalizado_correcto=False).order_by('-fecha_agregado')
    form = DocumentoForm()
    form_usuario = UsuariosForm(request.user)
    context = {'casos':casos, 
               'formDoc':form, 
               'form_usuario':form_usuario,
               'destino_resultados':'FrontEnd/resultados_caso.html',
               'destino_informes':'FrontEnd/informes_caso.html',
               'destino_documentos':'FrontEnd/documentos_caso.html',
               'title':'Casos',
               }
    return render(request,'FrontEnd/casos.html',context)

@login_required
def casos_finalizados(request):
    """Genera la vista de los casos finalizados de un usuario determinado"""
    
    casos = Caso.objects.filter(usuario=request.user).filter(eliminado=False).filter(Q(finalizado_correcto=True) | Q(finalizado_incorrecto=True)).order_by('-fecha_agregado')
    form_usuario = UsuariosForm(request.user)
    context = {'casos':casos, 
               'form_usuario':form_usuario,
               'destino_resultados':'FrontEnd/resultados_casofinalizado.html',
               'destino_informes':'FrontEnd/informes_casofinalizado.html',
               'destino_documentos':'FrontEnd/documentos_casofinalizado.html',
               'title':'Casos finalizados',
               }
    return render(request,'FrontEnd/casos_finalizados.html',context)

@login_required
def editar_caso(request,caso_id):
    """ Editar un caso ya existente"""
    caso = Caso.objects.get(id=caso_id)
    if request.method == 'POST':
        #Actualizar el caso
        form = CasoFormEdit(instance=caso, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('casos'))
    else:
        #Solicita el caso para ser modificado, con información precargada
        form = CasoFormEdit(instance=caso)
        
    context = {'form':form, 
               'caso': caso, 
               'caso_nombre':caso.nombre, 
               'documentos':documentos,
               'title':'Editar caso',
               }

    return render(request,'FrontEnd/editar_caso.html',context)


def eliminar_generico_casos(request,caso):
    """Función para eliminar casos"""
    if caso.propietario == request.user:
        documentos = Documento.objects.filter(caso=caso)
        for doc in documentos:
            parrafos = Parrafo.objects.filter(doc=doc)
            for parrafo in parrafos:
                parrafo.eliminado = True
                parrafo.save()
            entidades = EntidadesDoc.objects.filter(doc=doc)
            for entidad in entidades:
                entidad.eliminado = True
                entidad.save()
            tokens = TokensDoc.objects.filter(doc=doc)
            for token in tokens:
                token.eliminado = True
                token.save()
            notas = NotaDocumento.objects.filter(entidad=doc)
            for nota in notas:
                nota.eliminado = True
                nota.save()
            mensajes = Mensaje.objects.filter(documento=doc)
            for mensaje in mensajes:
                mensaje.eliminado = True
                mensaje.save()
            doc.eliminado = True
            doc.save()
        caso.eliminado = True
        caso.save()
    else:
        caso.usuario.remove(request.user.id)

@login_required
def eliminar_finalizado(request,caso_id):
    """Elimina un caso finalizado específico"""

    caso = Caso.objects.get(id=caso_id)
    eliminar_generico_casos(request,caso)

    return HttpResponseRedirect(reverse('casos_finalizados'))

@login_required
def administrar_casos(request,tipo):
    """Administrar casos seleccionados, para ser eliminados o finalizados"""
    if request.method == 'POST':
        ids = request.POST.getlist('checks[]')
        if tipo == "incorrecto":
            #Se han seleccionado casos para ser eliminados
            for id in ids:
                 caso = Caso.objects.filter(id=id)
                 for c in caso:
                    if c.propietario == request.user:
                        c.finalizado_incorrecto = True
                        c.save()
                    else:
                        c.usuario.remove(request.user.id)
        else:
            #Se han seleccionado casos para ser finalizados
            for id in ids:
                caso = Caso.objects.filter(id=id)
                for c in caso:
                    if c.propietario == request.user:
                        c.finalizado_correcto = True
                        c.save()
                    else:
                        c.usuario.remove(request.user.id)
    
    return HttpResponseRedirect(reverse('casos'))


@login_required
def nuevo_caso(request):
    """Crea un nuevo caso"""
    if request.method != 'POST':
        #No se ha enviado información, se crea una forma vacía
        form = CasoForm()
    else:
        #POST información recibida, se procesa la misma
        form = CasoForm(request.POST)
        if form.is_valid():
            nuevo_caso = form.save(commit=False)
            nuevo_caso.propietario = request.user
            nuevo_caso.eliminado = False
            nuevo_caso.finalizado_correcto = False
            nuevo_caso.finalizado_incorrecto = False
            nuevo_caso.save()
            nuevo_caso.usuario.add(request.user)
            return HttpResponseRedirect(reverse('casos'))

    context = {'form':form,
               'title':'Nuevo caso',
               }
    return render(request,'FrontEnd/nuevo_caso.html',context)

@login_required
def compartir_casos(request,caso_id,tipo):
    """Comparte un caso a otro usuario"""
    if request.method == 'POST':
        next = request.POST.get('next', '/')
        usuario = request.POST.get('usuarios')
        usuario_instance = User.objects.get(id=usuario)
        caso = Caso.objects.get(id=caso_id)
        if not(caso.usuario.filter(id=usuario_instance.id)):
            caso.usuario.add(usuario)
        if tipo=="con":
            if caso.propietario != usuario_instance:
                caso.propietario = usuario_instance
                caso.save()
        
    return HttpResponseRedirect(reverse(next))

@login_required
def compartir_casoFinalizado(request,caso_id):
    """Comparte un caso finalizado a otro usuario"""
    if request.method == 'POST':
        usuario = request.POST.get('usuarios')
        usuario_instance = User.objects.get(id=usuario)
        caso = Caso.objects.get(id=caso_id)
        if not(caso.usuario.filter(id=usuario_instance.id)):
            caso.usuario.add(usuario)

    return HttpResponseRedirect(reverse('casos_finalizados'))  
    

#***********************************************************************************************************************************************************************
#****************************************************************************************** END CASOS ******************************************************************
#***********************************************************************************************************************************************************************

#***********************************************************************************************************************************************************************
#****************************************************************************************** START NOTAS ****************************************************************
#***********************************************************************************************************************************************************************

@login_required
def notas(request, id, tipo):
    """Genera la vista de todas las notas"""
    notas = {
             "documento": NotaDocumento.objects.filter(entidad=id).filter(eliminado=False).order_by('-fecha_agregado'),
             "caso": NotaCaso.objects.filter(entidad=id).filter(eliminado=False).order_by('-fecha_agregado'),
             }
    context = { "notas" : notas[tipo],
                "id": id,
                "tipo": tipo,
                "title":'Notas',
                }
    if request.method != 'POST':
        form = NotaForm()
        if tipo == "documento":
            doc = Documento.objects.get(id=id)
            context['descripcion'] = doc.descripcion_doc
    else:
        crearNota = {
                    "documento": NotaDocumento,
                    "caso": NotaCaso,
            }
        form = NotaForm(request.POST)
        nueva_nota = form.save(commit=False)
        notaHija = crearNota[tipo](nota=nueva_nota.nota, descripcion=nueva_nota.descripcion, eliminado=False)
        if tipo == "documento":
            doc = Documento.objects.get(id=id)
            notaHija.entidad = doc
            context['descripcion'] = doc.descripcion_doc
        elif tipo == "caso":
            notaHija.entidad = Caso.objects.get(id=id)
        notaHija.save()
        return HttpResponseRedirect(reverse('notas',args=[id,tipo]))

    context['form'] = form
    
    return render(request,'FrontEnd/notas.html',context)
    
@login_required
def eliminar_nota(request,id,tipo,id_nota):
    """Elimina una nota desde la vista específica que muestra las notas de los casos o documentos"""
    if tipo == "documento":
        nota_eliminar = NotaDocumento.objects.get(id=id_nota)
    elif tipo == "caso":
        nota_eliminar = NotaCaso.objects.get(id=id_nota)
    nota_eliminar.eliminado = True
    nota_eliminar.save()
    return HttpResponseRedirect(reverse('notas',args=[id,tipo]))

@login_required
def eliminar_notacaso(request,id_caso,id_nota):
    """Elimina una nota de caso y retorna a la vista asociada a la sección de notas genérica"""
    form_elegir = BuscadorCasosForm(request.user)
    form_crear = NotaForm()
    caso = Caso.objects.get(id=id_caso)
    documentos = caso.documento_set.filter(eliminado=False).order_by('-fecha_agregado')
    notas = NotaCaso.objects.filter(entidad=id_caso).filter(eliminado=False).order_by('-fecha_agregado')
    context = {
                'form_elegir':form_elegir,
                'form_crear': form_crear,
                'id_caso' : id_caso,
                'documentos' : documentos,
                'inicial' : False,
                'notas' : notas,
               }
    nota_eliminar = NotaCaso.objects.get(id=id_nota)
    nota_eliminar.eliminado = True
    nota_eliminar.save()
    return render(request,'FrontEnd/ver_notas.html',context)

@login_required
def ver_notas(request):
    """Ver notas de casos o documentos"""
    form_elegir = BuscadorCasosForm(request.user)
    form_crear = NotaForm()
    context = {
                'form_elegir':form_elegir,
                'form_crear': form_crear,
                "title":'Notas de caso',
               }
    if request.method == 'POST':
        id_caso = request.POST.get('casos')
        caso = Caso.objects.get(id=id_caso)
        documentos = caso.documento_set.filter(eliminado=False).order_by('-fecha_agregado')
        notas = NotaCaso.objects.filter(entidad=id_caso).filter(eliminado=False).order_by('-fecha_agregado')
        context['id_caso'] = id_caso
        context['documentos'] = documentos
        context['inicial'] = False
        context['notas'] = notas
    return render(request,'FrontEnd/ver_notas.html',context)
 
@login_required
def crear_nota(request, id_caso):
    """Crea una nota a un caso"""
    caso = Caso.objects.get(id=id_caso)
    documentos = caso.documento_set.filter(eliminado=False).order_by('-fecha_agregado')
    notas = NotaCaso.objects.filter(entidad=id_caso).filter(eliminado=False).order_by('-fecha_agregado')
    form_elegir = BuscadorCasosForm(request.user)
    form_crear = NotaForm()
    context = {
            'form_elegir':form_elegir,
            'form_crear': form_crear,
            'id_caso': id_caso,
            'documentos': documentos,
            'notas': notas,
            'inicial': False,
        }
    if request.method == 'POST':
        form = NotaForm(request.POST)
        nueva_nota = form.save(commit=False)
        notaHija = NotaCaso(nota=nueva_nota.nota, descripcion=nueva_nota.descripcion, eliminado=False)
        notaHija.entidad = caso
        notaHija.save()
    return render(request,'FrontEnd/ver_notas.html',context)

#*********************************************************************************************************************************************************************
#****************************************************************************************** END NOTAS ****************************************************************
#*********************************************************************************************************************************************************************

#*********************************************************************************************************************************************************************
#**************************************************************************************START BÚSQUEDAS ***************************************************************
#*********************************************************************************************************************************************************************

@login_required
def buscador_general(request,caso_id):
    """Genera la vista para las búsquedas generales"""

    caso = Caso.objects.get(id=caso_id)
    context = {"caso":caso,
               'title':'Buscador general',
               }
    if request.method != "POST":
        #Solicita la página de búsqueda
        form = BuscadorGeneralForm()    
    else:
        #Busca en los documentos y retorna las apariciones
        
        form = BuscadorGeneralForm(request.POST)
        
        if form.is_valid():
            string = form.cleaned_data['busqueda']
            context["expresion"] = string
            documentos = caso.documento_set.all().order_by('-fecha_agregado')
            resultados = []
            id_fila = 0
            for documento in documentos:
                parrafos = Parrafo.objects.filter(doc=documento)
                for parrafo in parrafos:
                    aux = posiciones(parrafo.parrafo,string)
                    if len(aux) > 0:
                        resultados.append([documento.titulo,documento.id,parrafo.nro,parrafo.parrafo,aux,id_fila])
                        id_fila += 1
            context["res"] = resultados
            resultados_json = json.dumps(resultados)
            context["json"] = resultados_json
    context["form"] = form
    return render(request,'FrontEnd/buscador_general.html',context)

def posiciones(parrafo,palabra):
    """Obtiene las posiciones en las cuáles una palabra determinada aparece en un párrafo"""

    respuesta = []
    posicion_actual = 0
    palabra = palabra.lower()
    parrafo = parrafo.lower()
    aparicion = parrafo.find(palabra)
    long = len(palabra)
    while aparicion >= 0:
        respuesta.append(aparicion)
        posicion_actual = aparicion + long
        aparicion = parrafo.find(palabra,posicion_actual)
    return respuesta
    
@login_required
def buscador_inteligente(request,tipo,caso_id):
    """Genera la vista para las búsquedas inteligentes"""

    caso = Caso.objects.get(id=caso_id)
    if request.method == "POST":
        ids_eliminar = request.POST.getlist('checks2[]')
        for id in ids_eliminar:
             entidades = EntidadesDoc.objects.filter(id=id)
             for entidad in entidades:
                entidad.eliminado = True
                entidad.save()
    
    context = {"tipo":tipo,
                "caso_nombre":caso.nombre,
                "modelo":caso.modelo,
                "org":"Organizaciones",
                "loc":"Locaciones",
                "lex":"Léxicos detectados",
                "pers":"Personas",
                "drog":"Drogas",
                "econ":"Económicos",
                "caso_id":caso.id,
                'title':'Buscador inteligente',
                }
    documentos = caso.documento_set.all().order_by('-fecha_agregado')
    resultado = []
    if tipo == "Léxicos detectados":
        for documento in documentos:
            tokens = TokensDoc.objects.filter(doc=documento).filter(eliminado=False)
            for t in tokens:
                parrafo = Parrafo.objects.get(id=t.parrafo.id)
                resultado.append([t.aparicion,t.categoria,t.lema,t.tipo,t.frase,parrafo.nro,parrafo.parrafo,documento.id,documento.titulo,t.id])
    else:
        for documento in documentos:
            entidad = EntidadesDoc.objects.filter(doc=documento).filter(tipo=GetEntidad().getEntidad(tipo)).filter(eliminado=False)
            for e in entidad:
                parrafo = Parrafo.objects.get(id=e.parrafo.id)
                resultado.append([e.string, e.start, e.end, e.doc.id, documento.titulo, parrafo.nro, parrafo.parrafo, e.id, e.string_original])
    context["res"] = resultado
    resultados_json = json.dumps(resultado)
    context["json"] = resultados_json
    return render(request,'FrontEnd/buscador_inteligente.html', context)

@login_required
def buscador_guiado(request,tipo,caso_id):
    """Genera la vista para búsquedas guiadas"""

    expresiones_reg = {
            "Email": RegexEmail(),
            "Documento": RegexDocumento(),
            "Tarjeta": RegexTarjeta(),
            "Teléfono": RegexTelefono(),
            "URL": RegexUrl(),
        }
    caso = Caso.objects.get(id=caso_id)
    if request.method != "POST":
        context = {"tipo":tipo,
                   "caso_nombre":caso.nombre,
                   "email":"Email",
                   "dni":"Documento",
                   "tarjeta":"Tarjeta",
                   "telefono":"Teléfono",
                   "url": "URL",
                   "caso_id":caso.id,
                   'title':'Buscador guiado',
                   }
        if tipo in expresiones_reg:
            resultados = buscar_regex(tipo, caso, expresiones_reg)
            d_res = defaultdict(list)
            for resultado in resultados:
                d_res[resultado[2]].append((resultado[0],resultado[1],resultado[3],resultado[4],resultado[5],resultado[6]))
            #resultado[0]: documento.id; resultado[1]: documento.nombre_doc; resultado[2]: m.group; resultado[3]: m.start(); resultado[4]: m.end(); 
            #resultad[5]: parrafo.nro; resultado[6]: parrafo.parrafo
            resultados = dict(d_res)
            context["res"] = resultados
            resultados_json = json.dumps(resultados)
            context["json"] = resultados_json
    return render(request,'FrontEnd/buscador_guiado.html', context)

def buscar_regex(tipo, caso, expresiones_reg):
    """Busca dentro de un documento las expresiones regulares especificadas por parámetro"""
    regex = expresiones_reg[tipo]
    reg = regex.pattern
    documentos = caso.documento_set.all().order_by('-fecha_agregado')
    resultados = []
    for documento in documentos:
        parrafos = Parrafo.objects.filter(doc_id= documento.id)
        for parrafo in parrafos:
            for m in reg.finditer(parrafo.parrafo):
                resultados.append((documento.id, documento.titulo, m.group(), m.start(), m.end(), parrafo.nro, parrafo.parrafo))
    if tipo == "URL":
        resultados = [resultado for resultado in resultados if not(RegexEmail().pattern.match(resultado[2]))]
    return resultados

def guardar_resultadoGeneral(request,caso_id,expresion):
    """Guarda resultados de búsquedaa general"""
    if request.method == "POST":
        form = BuscadorGeneralForm()
        resultado_json = request.POST.get("resultado_json")
        resultado = json.loads(resultado_json)
        destacados = request.POST.getlist('checks3[]')
        caso = Caso.objects.get(id=caso_id)
        documentos = caso.documento_set.filter(eliminado=False)
        context = {'caso':caso,
                   'expresion':expresion,
                   'res':resultado,
                   'json':resultado_json,
                   'form':form,
                   'title':'Buscador general',
                   }
        resultado_header = ResultadoHeader(caso=caso,busqueda='General',tipo=expresion,estado=True,eliminado=False,propietario=request.user)
        resultado_header.save()
        for d in documentos:
            resultado_header.documentos.add(d)
        resultado_header.save()
        for fila in resultado:
            for aparicion in fila[4]:
                id = f'{fila[5]}.{aparicion}'
                documento = Documento.objects.get(id=fila[1])
                resultadoGen = ResultadoBusqGeneral(parrafo_nro=fila[2],posicion=aparicion,documento=documento,documento_nombre=fila[0],parrafo=fila[3],header=resultado_header)
                if id in destacados:
                    resultadoGen.destacado =True
                else:
                    resultadoGen.destacado = False
                resultadoGen.save()
        return render(request,'FrontEnd/buscador_general.html',context)
        
    return HttpResponseRedirect(reverse('buscador_general',args=[caso_id]))

def guardar_resultadoGuiado(request,tipo,caso_id):
    """Guarda resultados de búsqueda guiada"""
    if request.method == "POST":
        resultado_json = request.POST.get("resultado_json")
        resultado = json.loads(resultado_json)
        destacados = request.POST.getlist('checks3[]')
        caso = Caso.objects.get(id=caso_id)
        documentos = caso.documento_set.filter(eliminado=False)
        resultado_header = ResultadoHeader(caso=caso,busqueda='Guiada',tipo=tipo,estado=True,eliminado=False,propietario=request.user)
        resultado_header.save()
        for d in documentos:
            resultado_header.documentos.add(d)
        resultado_header.save()
        context = {"tipo":tipo,
                   "caso_nombre":caso.nombre,
                   "email":"Email",
                   "dni":"Documento",
                   "tarjeta":"Tarjeta",
                   "telefono":"Teléfono",
                   "url": "URL",
                   "caso_id":caso.id,
                   "res": resultado,
                   "title":'Buscador guiado',
                   "json":resultado_json,
                   }
        for key, value in resultado.items():
            header_general = ResultadoBusqGuiadaGeneral(clave=key,cantidadTotal=len(value),header=resultado_header)
            if key in destacados:
                header_general.destacado = True
            else:
                header_general.destacado = False
            header_general.save()
            for item in value:
                documento = Documento.objects.get(id=item[0])
                resultadoGui = ResultadoBusqGuiada(documento=documento,documento_nombre=item[1],start=item[2],end=item[3],parrafo_nro=item[4],parrafo=item[5],general=header_general)
                resultadoGui.save()
        return render(request,'FrontEnd/buscador_guiado.html', context)

        
    return HttpResponseRedirect(reverse('buscador_guiado',args=[tipo,caso_id]))


def guardar_resultadoInteligente(request,tipo,caso_id):
    """Guarda resultados de búsqueda inteligente"""
    if request.method == "POST":
        resultado_json = request.POST.get("resultado_json")
        resultado = json.loads(resultado_json)
        destacados = request.POST.getlist('checks3[]')
        caso = Caso.objects.get(id=caso_id)
        documentos = caso.documento_set.filter(eliminado=False)
        context = {"tipo":tipo,
                   "caso_nombre":caso.nombre,
                   "modelo":caso.modelo,
                   "org":"Organizaciones",
                   "loc":"Locaciones",
                   "lex":"Léxicos detectados",
                   "pers":"Personas",
                   "drog":"Drogas",
                   "econ":"Económicos",
                   "title":'Buscador inteligente',
                   "caso_id":caso.id,
                   "res":resultado,
                   "json":resultado_json,
                   }
        resultado_header = ResultadoHeader(caso=caso,busqueda='Inteligente',tipo=tipo,estado=True,eliminado=False,propietario=request.user)
        resultado_header.save()
        for d in documentos:
            resultado_header.documentos.add(d)
        resultado_header.save()
        for item in resultado:
            if tipo != "Léxicos detectados":
                entidad = EntidadesDoc.objects.get(id=item[7])
                resultadoInt = ResultadoBusqInteligente(doc=entidad.doc,string=entidad.string,string_original=entidad.string_original,start=entidad.start,end=entidad.end,parrafo_nro=entidad.parrafo.nro,parrafo=entidad.parrafo.parrafo,header=resultado_header)
                id = item[7] 
            else:
                token = TokensDoc.objects.get(id=item[9])
                resultadoInt = ResultadoBusqInteligenteTokens(doc=token.doc,aparicion=token.aparicion,tipo=token.tipo,frase=token.frase,lema=token.lema,categoria=token.categoria,parrafo=token.parrafo,parrafo_nro=token.parrafo.nro,header=resultado_header)
                id = item[9]
            if str(id) in destacados:
                resultadoInt.destacado = True
            else:
                resultadoInt.destacado = False
            resultadoInt.save()
        return render(request,'FrontEnd/buscador_inteligente.html', context)


    return HttpResponseRedirect(reverse('buscador_inteligente',args=[tipo,caso_id]))

@login_required
def editar_entidad(request,tipo,id_ent,id_caso):
    """Editar entidad"""
    if request.method == 'POST':
        string = request.POST.get('string')
        entidad = EntidadesDoc.objects.get(id=id_ent)
        entidad.string = string
        entidad.save()
    return HttpResponseRedirect(reverse('buscador_inteligente',args=[tipo,id_caso]))


#*********************************************************************************************************************************************************************
#**************************************************************************************END BÚSQUEDAS *****************************************************************
#*********************************************************************************************************************************************************************

#*********************************************************************************************************************************************************************
#************************************************************************************** START RESULTADOS *************************************************************
#*********************************************************************************************************************************************************************

def generar_resultados(request,id_caso):
    """Genera los resultados para mostrar en las vistas"""
    caso = Caso.objects.get(id=id_caso)
    resultados = caso.resultadoheader_set.filter(eliminado=False).filter(propietario=request.user).order_by('-fecha')
    flag = False
    for resultado in resultados:
        if resultado.estado:
            documentos = caso.documento_set.filter(eliminado=False).values_list('id', flat=True)
            documentos_res = resultado.documentos.all().values_list('id',flat=True)
            if set(documentos) != set(documentos_res):
                flag = True
                resultado.estado = False
                resultado.save()
    if flag:
        resultados = caso.resultadoheader_set.filter(eliminado=False).order_by('-fecha')

    return resultados

@login_required
def resultados(request):
    """Resultados de las búsquedas"""
    form_elegir = BuscadorCasosForm(request.user)
    context = {
                'form_elegir':form_elegir,
                'title':'Resultados',
               }
    if request.method == 'POST':
        caso_id = request.POST.get('casos')
        resultados = generar_resultados(request,caso_id)
        context['resultados'] = resultados
        context['caso_id'] = caso_id
        context['inicial'] = False

    return render(request,'FrontEnd/resultados.html', context)

@login_required
def resultados_caso(request,caso_id,destino):
    """Resultados de un único caso específico"""
    context = {
                'title':'Resultados caso',
               }
    resultados = generar_resultados(request,caso_id)
    context['resultados'] = resultados
    context['caso_id'] = caso_id

    return render(request,destino, context)

def eliminar_general_resultado(resultado_id,tipo):
    """Elimina resultados"""

    resultado = ResultadoHeader.objects.get(id=resultado_id)
    resultado.eliminado = True
    resultado.save()

    tipo_eliminar = {
            "Guiada":ResultadoBusqGuiadaGeneral,
            "General":ResultadoBusqGeneral,
            "Inteligente":ResultadoBusqInteligente,
        }

    #Eliminar físicamente todas las tuplas asociadas al resultado
    tuplas = tipo_eliminar[tipo].objects.filter(header=resultado)
    for tupla in tuplas:
        if tipo == "Guiada":
            guiadas = ResultadoBusqGuiada.objects.filter(general=tupla)
            guiadas.delete()
        tupla.delete()


@login_required
def eliminar_resultado(request,caso_id,resultado_id,tipo):
    """Elimina resultado de búsqueda"""

    eliminar_general_resultado(resultado_id,tipo)

    resultados = generar_resultados(request,caso_id)
    form_elegir = BuscadorCasosForm(request.user)
    context = { 
                'title':'Resultados',
                'form_elegir':form_elegir,
                'resultados':resultados,
                'inicial':False,
                'caso_id': caso_id,
               }

    return render(request,'FrontEnd/resultados.html', context)

@login_required
def eliminar_resultadoCaso(request,caso_id,resultado_id,tipo):
    """Elimina resultado de búsqueda"""

    eliminar_general_resultado(resultado_id,tipo)
    resultados = generar_resultados(request,caso_id)
    context = {
                'title':'Resultados',
                'resultados':resultados,
                'caso_id':caso_id,
               }

    return render(request,'FrontEnd/resultados_caso.html', context)

@login_required
def ver_resultado(request,resultado_id,tipo):
    """Ver resultados específicos asociados a una búsqueda"""

    lexicos = "Léxicos detectados"
    resultado = ResultadoHeader.objects.get(id=resultado_id)
    context = {
                'header':resultado,
            }
    tipo_ver = {
            "Guiada":ResultadoBusqGuiadaGeneral,
            "General":ResultadoBusqGeneral,
            "Inteligente":ResultadoBusqInteligente,
        }

    if tipo == "Guiada":
        tuplas = tipo_ver[tipo].objects.filter(header=resultado)
        aux = []
        for tupla in tuplas:
            guiadas = ResultadoBusqGuiada.objects.filter(general=tupla)
            aux_guiadas = []
            for guiada in guiadas:
                aux_guiadas.append([guiada.documento.id,guiada.documento_nombre,guiada.start,guiada.end,guiada.parrafo,guiada.parrafo_nro])
            aux.append([tupla.clave,tupla.destacado,tupla.cantidadTotal,aux_guiadas])

        context['tuplas'] = aux
        context['title'] = 'Resultado guiado'
        return render(request,'FrontEnd/resultados_guiado.html', context)
    else:
        if resultado.tipo == lexicos:
            tuplas = ResultadoBusqInteligenteTokens.objects.filter(header=resultado)
            next = 'FrontEnd/resultados_inteligente_tokens.html'
        else:
            tuplas = tipo_ver[tipo].objects.filter(header=resultado)
            next = 'FrontEnd/resultados_inteligente.html'
        context['tuplas'] = tuplas

        if tipo == "Inteligente":
            context['title'] = 'Resultado inteligente'
            return render(request,next, context)
        else:
            context['title'] = 'Resultado general'
            return render(request,'FrontEnd/resultados_general.html', context)

        
#*********************************************************************************************************************************************************************
#************************************************************************************** END RESULTADOS ***************************************************************
#*********************************************************************************************************************************************************************


#*********************************************************************************************************************************************************************
#************************************************************************************** START INFORMES ***************************************************************
#*********************************************************************************************************************************************************************

@login_required
def crearInforme(request,resultado_id,tipo_informe):
    """Crea informe en base a información de los resultados"""

    lexicos = "Léxicos detectados"

    resultado = ResultadoHeader.objects.get(id=resultado_id)
    busqueda = resultado.busqueda

    filepath = f'{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}\informes'

    document = Document()
    style = document.styles['Normal']
    font = style.font
    font.name = 'Arial'

    document.add_heading('Informe de búsqueda',0)

    busq = f'Búsqueda {busqueda}'
    p_usuario = document.add_paragraph('Usuario: ')
    p_usuario.add_run(request.user.username).italic = True
    paragraph_format = p_usuario.paragraph_format
    paragraph_format.space_before = Pt(50)
    p = document.add_paragraph('Informe generado en base a resultados obtenidos mediante una ')
    p.add_run(busq).italic = True
    p.add_run(' sobre el caso ')
    p.add_run(resultado.caso.nombre).italic = True
    p.add_run('.')
    p.style.font.size = Pt(13)
    
    p2 = document.add_paragraph('Fecha de búsqueda: ')
    p2.add_run(str(resultado.fecha.strftime("%d-%m-%Y %H:%M:%S")))

    p3 = document.add_paragraph('Las apariciones en ')
    p3.add_run('negrita').bold = True
    p3.add_run(' son aquellas que han sido señaladas como destacadas.')
    paragraph_format2 = p3.paragraph_format
    paragraph_format2.space_after = Pt(50)

    document.add_paragraph(f'"{resultado.tipo}"')

    tipo_busq = {
            "Guiada":ResultadoBusqGuiadaGeneral,
            "General":ResultadoBusqGeneral,
            "Inteligente":ResultadoBusqInteligente,
        }

    if tipo_informe == "destacados":
        if resultado.tipo != lexicos:
            tuplas = tipo_busq[busqueda].objects.filter(header=resultado).filter(destacado=True)
        else:
            tuplas = ResultadoBusqInteligenteTokens.objects.filter(header=resultado).filter(destacado=True)
    else:
        if resultado.tipo != lexicos:
            tuplas = tipo_busq[busqueda].objects.filter(header=resultado)
        else:
            tuplas = ResultadoBusqInteligenteTokens.objects.filter(header=resultado)

    if busqueda == "Guiada":
        for tupla in tuplas:
            guiadas = ResultadoBusqGuiada.objects.filter(general=tupla)
            if tupla.destacado:
                p4 = document.add_paragraph()
                p4.add_run(tupla.clave).bold = True
            else:
                p4 = document.add_paragraph(tupla.clave)
            paragraph_format = p4.paragraph_format
            paragraph_format.space_before = Pt(50)
            t = document.add_paragraph('Cantidad de apariciones: ')
            t.add_run(str(tupla.cantidadTotal))
            table = document.add_table(1,4)
            table.style = 'TableGrid'
            heading_cells = table.rows[0].cells
            heading_cells[0].text = 'Documento'
            heading_cells[1].text = 'Nro. párrafo'
            heading_cells[2].text = 'Pos. inicial'
            heading_cells[3].text = 'Pos. final'
            for guiada in guiadas:
                cells = table.add_row().cells
                cells[0].text = guiada.documento_nombre
                cells[1].text = str(guiada.parrafo_nro)
                cells[2].text = str(guiada.start)
                cells[3].text = str(guiada.end)
    else:
        
        if busqueda == "Inteligente":
            if resultado.tipo != lexicos:
                table = document.add_table(1, 5)
                table.style = 'TableGrid'
                table.autofit = True
                heading_cells = table.rows[0].cells
                heading_cells[0].text = 'Aparición'
                heading_cells[1].text = 'Nro. párrafo'
                heading_cells[2].text = 'Pos. inicial'
                heading_cells[3].text = 'Pos. final'
                heading_cells[4].text = 'Documento'
                for tupla in tuplas:
                    cells = table.add_row().cells
                    if tupla.destacado:
                        cells[0].paragraphs[0].add_run(tupla.string).bold=True
                    else:
                        cells[0].text = tupla.string
                    cells[1].text = str(tupla.parrafo_nro)
                    cells[2].text = str(tupla.start)
                    cells[3].text = str(tupla.end)
                    cells[4].text = str(tupla.doc.titulo)
            else:
                table = document.add_table(1, 6)
                table.style = 'TableGrid'
                table.autofit = True
                heading_cells = table.rows[0].cells
                heading_cells[0].text = 'Aparición'
                heading_cells[1].text = 'Base léxica'
                heading_cells[2].text = 'Categoría'
                heading_cells[3].text = 'Tipo'
                heading_cells[4].text = 'Documento'
                heading_cells[5].text = 'Nro. párrafo'
                for tupla in tuplas:
                    cells = table.add_row().cells
                    if tupla.destacado:
                        cells[0].paragraphs[0].add_run(tupla.aparicion).bold=True
                    else:
                        cells[0].text = tupla.aparicion
                    cells[1].text = str(tupla.lema)
                    cells[2].text = str(tupla.categoria)
                    cells[3].text = str(tupla.tipo)
                    cells[4].text = str(tupla.doc.titulo)
                    cells[5].text = str(tupla.parrafo_nro)

        else:
            table = document.add_table(1, 4)
            table.style = 'TableGrid'
            table.autofit = True
            heading_cells = table.rows[0].cells
            heading_cells[0].text = 'Aparición'
            heading_cells[1].text = 'Nro. párrafo'
            heading_cells[2].text = 'Pos. inicial'
            heading_cells[3].text = 'Documento'
            for tupla in tuplas:
                cells = table.add_row().cells
                if tupla.destacado:
                    cells[0].paragraphs[0].add_run(resultado.tipo).bold=True
                else:
                    cells[0].text = resultado.tipo
                cells[1].text = str(tupla.parrafo_nro)
                cells[2].text = str(tupla.posicion)
                cells[3].text = str(tupla.documento_nombre)
    
    informe = Informe(caso=resultado.caso,eliminado=False,busqueda=resultado.busqueda,propietario=request.user)
    informe.save()

    fecha = informe.fecha.strftime("%d-%m-%Y-%H-%M-%S")
    id = informe.id

    dominio = f'{filepath}\{id}-{fecha}.docx'

    informe.path = dominio
    informe.save()

    document.save(dominio)

    return HttpResponseRedirect(reverse('ver_resultado',args=[resultado_id,busqueda]))

@login_required
def informes(request):
    """Muestra todos los informes para poder ser descargados"""
    form = BuscadorCasosForm(request.user)
    context = {'form':form, 
               'title':'Informes'
               }
    if request.method == 'POST':
        id_caso = request.POST.get('casos')
        caso = Caso.objects.get(id=id_caso)
        informes = Informe.objects.filter(caso=caso).filter(eliminado=False).filter(propietario=request.user).order_by('-fecha')
        context['id_caso'] = id_caso
        context['informes'] = informes
        context['inicial'] = False
    return render(request,'FrontEnd/informes.html',context)

@login_required
def informes_caso(request,caso_id,destino):
    """Muestra todos los informes, de un caso determinado, para poder ser descargados"""
    context = { 
               'title':'Informes'
               }
    caso = Caso.objects.get(id=caso_id)
    informes = Informe.objects.filter(caso=caso).filter(eliminado=False).filter(propietario=request.user).order_by('-fecha')
    context['id_caso'] = caso_id
    context['informes'] = informes
    return render(request,destino,context)

@login_required
def ver_informe(request, id_informe):
    """Descarga el informe para que el usuario pueda leerlo desde su dispositivo"""
    informe = Informe.objects.get(id=id_informe)
    nombre = f'Informe-{informe.fecha.strftime("%d-%m-%Y %H:%M:%S")}.docx'
    with open(informe.path, 'rb') as file:
        response = HttpResponse(file.read(), content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        response['Content-Disposition'] = 'attachment; filename=%s' % nombre
        return response
    raise Http404

@login_required
def eliminar_informe(request,informe_id):
    """Elimina informe"""
    
    if request.method == 'POST':
        next = request.POST.get('next', '/')

    informe = Informe.objects.get(id=informe_id)
    informe.eliminado = True
    informe.save()

    informes = Informe.objects.filter(caso=informe.caso).filter(eliminado=False).order_by('-fecha')
    context = { 
               'title':'Informes',
               'id_caso':informe.caso,
               'informes':informes,
               }

    return render(request,next, context)


#*********************************************************************************************************************************************************************
#************************************************************************************** END INFORMES *****************************************************************
#*********************************************************************************************************************************************************************

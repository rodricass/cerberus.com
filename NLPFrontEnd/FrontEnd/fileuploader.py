import hashlib
import re
import time

from django.http import Http404

from .forms import DocumentoForm
from .genericos import ExtensionArchivo
from .models import Documento, Parrafo, EntidadesDoc, TokensDoc, Caso
from .genericos import TipoModelo
#from nlp_model_gen_plugins.plugins.whatsappPlugin import get_whatsapp_extract

class ObtenerCreador:
    """Clase que sirve para obtener la instancia correcta con la cual cargar un archivo, dependiendo de la fuente de la que venga"""

    def creadorArchivo(self,tipo,request,caso_id):
    #Si se agrega un formato nuevo de tipo de archivo que desee procesar de manera distinta, agregar al diccionario 'tipos_archivos' y crear la clase correspondiente en 'fileuploader.py'
        
        tipos_creadores = {
                    'UFED':CargarArchivoUFED,
                    'OTROS':CargarArchivoGeneral,
                }
    
        if tipo in tipos_creadores.keys():
            return tipos_creadores[tipo](request,caso_id)
        else: 
            raise Http404(f'Tipo de archivo {tipo} inexistente')

class CargarArchivo:

    def __init__(self,request,caso_id):
        """Clase encargada de cargar los archivos al sistema"""
        caso = Caso.objects.get(id=caso_id)
        self.modelo = TipoModelo().getModelo(caso.modelo)
        self.caso_id = caso_id
        self.user = request.user
        self.form = DocumentoForm(request.POST,request.FILES)
        self.files = request.FILES.getlist('documento')
        

class CargarArchivoUFED(CargarArchivo):

    def __init__(self,request,caso_id):
        """Clase encargada de cargar archivos UFED al sistema"""
        super().__init__(request,caso_id)

    def cargar(self):
        """Verifica la forma y carga cada uno de los archivos al sistema"""
        if self.form.is_valid():
            crear_documento_UFED(self.files)

    def crear_documento_UFED(self,files):
        """Crea y guarda documento en base a forma"""
        wpp = get_whatsapp_extract(files,self.user,self.modelo.model)
        while not wpp.is_analysed():
                time.sleep(0.1)
        results = wpp.get_positives_results()
        print("deberia imprimir los resultados")
        print(results)



class CargarArchivoGeneral(CargarArchivo):

    def __init__(self,request,caso_id):
        """Clase encargada de cargar archivos UFED al sistema"""
        super().__init__(request,caso_id)

    def cargar(self):
        """Verifica la forma y carga cada uno de los archivos al sistema"""
        if self.form.is_valid():
            for f in self.files:
                self.crear_documento_general(f)
    
    def crear_documento_general(self,file):
        """Crea y guarda documento en base a forma"""
    
        #Crea los hashs en base al contenido del documento
        hash_md5 = hashlib.md5()
        hash_sha = hashlib.sha1()
        for c in file.chunks():
            hash_md5.update(c)
            hash_sha.update(c)

        hash_md5 = hash_md5.hexdigest()
        hash_sha1 = hash_sha.hexdigest()
        propietario_doc = self.user

        #Parsea el documento en base a si es txt o docx
        nombre, punto, ext = file.name.rpartition(".")
        ext = ext.lower()
        
        lector = ExtensionArchivo().getLector(ext,file)
        texto = lector.read()

        nuevo_doc = Documento(titulo=file.name,nombre_doc=file.name,documento=file,texto=texto,propietario_doc=propietario_doc,hash_md5=hash_md5,hash_sha1=hash_sha1,eliminado=False)
        nuevo_doc.save()

        #Divide al documento en párrafos para mejor procesamiento
        self.dividirParrafos(nuevo_doc)

        #Crea las entidades correspondientes a los párrafos del documento
        self.crearEntidades(nuevo_doc)

        #Relaciona el documento con el usuario que lo está utilizando y con el caso correspondiente
        nuevo_doc.usuario.add(self.user)
        nuevo_doc.caso.add(self.caso_id)

        nuevo_doc.save()
    
    def  dividirParrafos(self,documento):
        """Segmenta el texto de un documento para ser almacenado por párrafos"""
        texto = documento.texto
        parrafos = texto.split("\n\n")
        i = 1
        for p in parrafos:
            parrafo = Parrafo(nro=i, doc_id=documento.id, parrafo=p, eliminado=False)
            parrafo.save()
            i = i + 1

    def crearEntidades(self,documento):
        """Crea las entidades en base al análisis nlp de un documento"""
        rx = re.compile("\s+")
        parrafos = Parrafo.objects.filter(doc_id=documento)
        resultado_tokenizer = []
        resultado_ner = []
        for parrafo in parrafos:
            entidades = []
            texto = rx.sub(" ", parrafo.parrafo)
            task_id = self.modelo.analyze(texto)
            while not self.modelo.is_analysis_ready(task_id):
                time.sleep(0.1)
            results = self.modelo.get_task_results(task_id)
            tokens = results['tokenizer_results']
            for token in [token.to_dict() for token in tokens]:
                resultado_tokenizer.append([token['base_form'],token['part_of_speech'],token['sentence'],token['token_text'],token['analysis_result']['category_detected'],parrafo.id])
            entidades = results['ner_results']
            for entidad in [entidad.to_dict() for entidad in entidades]:
                resultado_ner.append([entidad['text'],entidad['start_pos'],entidad['end_pos'],entidad['label'],parrafo.id])
        
        for entidad in resultado_ner:
            parrafo = Parrafo.objects.get(id=entidad[4])
            ent_aux = EntidadesDoc(doc=documento, tipo=entidad[3], string=entidad[0], string_original=entidad[0], start=entidad[1], end=entidad[2], parrafo=parrafo, eliminado=False)
            ent_aux.save()

        for token in resultado_tokenizer:
            parrafo = Parrafo.objects.get(id=token[5])
            token_aux = TokensDoc(doc=documento, aparicion=token[3], tipo=GetTipoToken().getTipoToken(token[1]), frase=token[2], lema=token[0], categoria=token[4], parrafo=parrafo, eliminado=False)
            token_aux.save()
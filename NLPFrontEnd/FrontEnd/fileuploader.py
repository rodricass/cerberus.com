import hashlib
import re
import time
import io

from django.http import Http404
from collections import defaultdict


from .forms import DocumentoForm
from .genericos import ExtensionArchivo
from .models import Documento, Parrafo, EntidadesDoc, TokensDoc, Investigacion
from .genericos import TipoModelo, GetTipoToken
from .myclasses import nlp
from nlp_model_gen_plugins.plugins.whatsappPlugin.whatsappPlugin import get_whatsapp_extract

class ObtenerCreador:
    """Clase que sirve para obtener la instancia correcta con la cual cargar un archivo, dependiendo de la fuente de la que venga"""

    def creadorArchivo(self,tipo,request,investigacion_id):
    #Si se agrega un formato nuevo de tipo de archivo que desee procesar de manera distinta, agregar al diccionario 'tipos_archivos' y crear la clase correspondiente en 'fileuploader.py'
        
        tipos_creadores = {
                    'UFED':CargarArchivoUFED,
                    'OTROS':CargarArchivoGeneral,
                }
    
        if tipo in tipos_creadores.keys():
            return tipos_creadores[tipo](request,investigacion_id)
        else: 
            raise Http404(f'Tipo de archivo {tipo} inexistente')

class CargarArchivo:

    def __init__(self,request,investigacion_id):
        """Clase encargada de cargar los archivos al sistema"""
        investigacion = Investigacion.objects.get(id=investigacion_id)
        self.modelo = TipoModelo().getModelo(investigacion.modelo)
        self.investigacion_id = investigacion_id
        self.user = request.user
        self.form = DocumentoForm(request.POST,request.FILES)
        self.files = request.FILES.getlist('documento')
        

class CargarArchivoUFED(CargarArchivo):

    def __init__(self,request,investigacion_id):
        """Clase encargada de cargar archivos UFED al sistema"""
        super().__init__(request,investigacion_id)

    def cargar(self):
        """Verifica la forma y carga cada uno de los archivos al sistema"""
        if self.form.is_valid():
            self.crear_documento_UFED()

    def crear_documento_UFED(self):
        """Crea y guarda documento en base a forma"""
        f = []
        for file in self.files:
            file.seek(0)
            data = file.read()
            if isinstance(data, bytes):
                data = data.decode("utf-8")
            myfile = io.StringIO(data)
            myfile.name = file.name
            myfile.data_encode = data
            myfile.doc_uploaded = file
            f.append(myfile)
        wpp = get_whatsapp_extract(f,nlp,self.modelo.model)

        while not (wpp.get_status()["is_analyzed"] or wpp.get_status()["has_error"]):
                time.sleep(0.1)
        if wpp.get_status()["has_error"]:
            raise Http404("Error al procesar la solicitud")

        results = wpp.get_positives_results()

        print(results)

        d_res = defaultdict(list)
        for resultado in results:
            r = {"from":resultado['from'],
                 "timestamp":resultado['timestamp'],
                 "content":resultado['content'],
                 "analysis_task_id":resultado['analysis_task_id'],
                 "analysis_result":resultado['analysis_result']}
            d_res[resultado['filename']].append(r)

        for file in f:

            texto = file.read()

            hash_md5 = hashlib.md5()
            hash_sha = hashlib.sha1()
            
            hash_md5.update(file.data_encode.encode('utf-8'))
            hash_sha.update(file.data_encode.encode('utf-8'))
            hash_md5 = hash_md5.hexdigest()
            hash_sha1 = hash_sha.hexdigest()

            propietario_doc = self.user

            #Parsea el documento en base a si es txt o docx
            nombre, punto, ext = file.name.rpartition(".")
            ext = ext.lower()

            nuevo_doc = Documento(nombre_doc=file.name,documento=file.doc_uploaded,texto=texto,propietario_doc=propietario_doc,hash_md5=hash_md5,hash_sha1=hash_sha1,eliminado=False)
            nuevo_doc.save()

            #Relaciona el documento con el usuario que lo está utilizando y con la investigación correspondiente
            nuevo_doc.usuario.add(self.user)
            nuevo_doc.investigacion.add(self.investigacion_id)

            nuevo_doc.save()

            tuplas = d_res[file.name]

            #Crea los párrafos correspondientes al documento
            for index,tupla in enumerate(tuplas):
                parrafo = Parrafo(nro=index, doc_id=nuevo_doc.id, parrafo=tupla['content'], eliminado=False)
                parrafo.save()
                self.crearEntidadesWPP(tupla['analysis_result'],nuevo_doc,parrafo)


    def crearEntidadesWPP(self,results,documento,parrafo):
        """Analiza los resultados obtenidos mediante el parseador de wpp y crea las entidades y tokens"""
        if not results['error']:
            if results['ner_positive']:
                for n in results['ner_results']:
                    ent_aux = EntidadesDoc(doc=documento, tipo=n['label'], string=n['text'], string_original=n['text'], start=n['start_pos'], end=n['end_pos'], parrafo=parrafo, incorrecta=False, eliminado=False)
                    ent_aux.save()
            if results['tokenizer_positive']:
                for t in results['tokenizer_results']:
                    token_aux = TokensDoc(doc=documento, aparicion=t['token_text'],tipo=GetTipoToken().getTipoToken(t['part_of_speech']),frase=t['sentence'],lema=t['base_form'],categoria=t['analysis_result']['category_detected'],parrafo=parrafo, eliminado=False)
                    token_aux.save()



class CargarArchivoGeneral(CargarArchivo):

    def __init__(self,request,investigacion_id):
        """Clase encargada de cargar archivos UFED al sistema"""
        super().__init__(request,investigacion_id)

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

        nuevo_doc = Documento(nombre_doc=file.name,documento=file,texto=texto,propietario_doc=propietario_doc,hash_md5=hash_md5,hash_sha1=hash_sha1,eliminado=False)
        nuevo_doc.save()

        #Divide al documento en párrafos para mejor procesamiento
        self.dividirParrafos(nuevo_doc)

        #Crea las entidades correspondientes a los párrafos del documento
        self.crearEntidades(nuevo_doc)

        #Relaciona el documento con el usuario que lo está utilizando y con la investigación correspondiente
        nuevo_doc.usuario.add(self.user)
        nuevo_doc.investigacion.add(self.investigacion_id)

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
            ent_aux = EntidadesDoc(doc=documento, tipo=entidad[3], string=entidad[0], string_original=entidad[0], start=entidad[1], end=entidad[2], parrafo=parrafo, incorrecta=False, eliminado=False)
            ent_aux.save()

        for token in resultado_tokenizer:
            parrafo = Parrafo.objects.get(id=token[5])
            token_aux = TokensDoc(doc=documento, aparicion=token[3], tipo=GetTipoToken().getTipoToken(token[1]), frase=token[2], lema=token[0], categoria=token[4], parrafo=parrafo, eliminado=False)
            token_aux.save()
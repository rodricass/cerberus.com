"""
Definition of models.
"""

import os

from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from simple_history.models import HistoricalRecords

from .genericos import TipoModelo, TipoArchivo

# Create your models here.

class Caso(models.Model):
    """Casos o investigaciones en curso"""

    #Nombre asociado al caso
    nombre = models.CharField(max_length=100)

    #Identificador específico del caso
    identificador = models.CharField(max_length=40, unique=True)

    #Descripción del caso
    descripcion = models.TextField()

    #Propietario del caso
    propietario = models.ForeignKey(User, related_name="propietario_caso")

    #Usuarios del caso
    usuario = models.ManyToManyField(User)

    #Fecha en que se creó el caso
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    #Eliminado lógico
    eliminado = models.BooleanField()    

    #Si el caso está finalizado correctamente o no
    finalizado_correcto = models.BooleanField()

    #Si el caso está finalizado incorrectamente o no
    finalizado_incorrecto = models.BooleanField()

    #Modelo que se utilizará a lo largo del caso para hacer las búsquedas inteligentes
    MODEL_CHOICES = TipoModelo().getModelChoices()
    modelo = models.CharField(max_length=10, choices=MODEL_CHOICES, default=MODEL_CHOICES[0])

    history = HistoricalRecords()

    def __str__(self):
        """Devuelve una frase representativa del modelo"""
        return self.nombre

class Documento(models.Model):
    """Documento relacionado a una investigación, o varias"""
    def directorio(self, filename):
        _datetime = datetime.now()
        datetime_str = _datetime.strftime("%Y-%m-%d-%H-%M-%S")
        ## if there are more than one dots
        #file_name_split = filename.split('.')
        #file_name_list = file_name_split[:-1]
        #ext = file_name_split[-1]
        #file_name_wo_ext = '.'.join(file_name_list)
        #name = '{0}-{1}.{2}'.format(file_name_wo_ext, datetime_str, ext)
        
        nombre, punto, ext = filename.rpartition(".")
        if not punto:
            ext = ""
        name = f'{self.hash_sha1}-{datetime_str}{punto}{ext}'
        return name

    #Nombre original del documento obtenido en base al archivo subido
    nombre_doc = models.CharField(max_length=100)

    #Título puesto por el usuario
    titulo = models.CharField(max_length=100)

    #Descripción breve del documento
    descripcion_doc = models.TextField(blank='True')

    #Dirección donde será almacenado el documento en el servidor
    documento = models.FileField(upload_to=directorio)

    #Texto extraído del documento guardado en disco
    texto = models.TextField()

    #Tipo que determina como debe ser procesado a futuro el archivo
    TIPO_CHOICES = TipoArchivo().getTipoArchivoChoices()
    tipo_archivo = models.CharField(max_length=20, choices=TIPO_CHOICES, default=TIPO_CHOICES[0])

#************************************************************************************************************************************

    #AUNQUE CADA DOCUMENTO ÚNICAMENTE SE ENCUENTRA ASOCIADO A UN CASO Y A UN USUARIO (PROPIETARIO SIEMPRE), SE DEJA EL CÓDIGO PARA QUE
    #SEA POSIBLE EXPANDIRLO A LA POSIBILIDAD EN QUE LOS DOCUMENTOS SE ENCUENTREN COMPARTIDOS ENTRE CASOS  

    #El propietario del documento solamente se utiliza para seguimiento de la cadena de custodia de los documentos,
    #un documento puede encontrarse en varios casos, con lo cual su propietario no tiene porque coincidir obligatoriamente 
    #con el del propietario del caso.
    propietario_doc = models.ForeignKey(User, related_name="propietario_user")

    #Usuarios del documento
    usuario = models.ManyToManyField(User)

    #Casos a los que pertenece el documento
    caso = models.ManyToManyField(Caso, blank=True)

    #Hash md5 del documento para asegurar integridad y para verificas si el documento ya existe dentro del sistema
    hash_md5 = models.CharField(max_length=32)

    #Hash sha1 del documento para asegurar integridad y para verificas si el documento ya existe dentro del sistema
    hash_sha1 = models.CharField(max_length=50)

#*************************************************************************************************************************************

    #Fecha en que se adjunto el documento a un caso
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    #Eliminado lógico
    eliminado = models.BooleanField()
    
    history = HistoricalRecords()

    def __str__(self):
        """Devuelve una frase representativa del modelo"""
        return self.titulo

class Parrafo(models.Model):
    """Entidad que almacena un párrafo de un texto de determinado documento"""
    
    #Párrafo específico
    parrafo = models.TextField(null=True)

    #Documento al que pertenece el párrafo
    doc = models.ForeignKey(Documento)

    #Número del párrafo dentro del texto
    nro = models.IntegerField()

    #Los párrafos son eliminados cuando se elimina el documento
    eliminado = models.BooleanField()

    history = HistoricalRecords()

    def __str__(self):
        """Devuelve una frase representativa del modelo"""
        return self.parrafo

class EntidadesDoc(models.Model):
    """Entidad obtenida en base a los resultados del ner generado en un análisis NLP de un documento"""

    #Documento en base al cual se ha obtenido la entidad
    doc = models.ForeignKey(Documento)
    
    #Tipo de entidad
    tipo = models.CharField(max_length=50)

    #Texto relacionado a la entidad
    string = models.CharField(max_length=100)

    #Texto relacionado a la entidad que ha sido editado
    string_original = models.CharField(max_length=100)

    #Comienzo del string
    start = models.IntegerField()

    #Final del string en cantidad de tokens
    end = models.IntegerField()

    #Párrafo del texto al que pertence la entidad
    parrafo = models.ForeignKey(Parrafo, null=True)

    #Eliminado lógico de una entidad 
    eliminado = models.BooleanField()

    history = HistoricalRecords()

    def __str__(self):
        """Devuelve una frase representativa del modelo"""
        return self.string

class TokensDoc(models.Model):
    """Entidad obtenida en base a los resultados del tokenizer generado en un análisis NLP de un documento"""

    #Documento en el cual se ha obtenido la entidad
    doc = models.ForeignKey(Documento)

    #Aparición
    aparicion = models.CharField(max_length=50)

    #Sustantivo/Verbo
    tipo = models.CharField(max_length=10)

    #Frase completa
    frase = models.CharField(max_length=150)

    #Lema en la que se basa la aparición
    lema = models.CharField(max_length=50)

    #Categoría a la que pertenece la palabra detectada
    categoria = models.CharField(max_length=50)

    #Párrafo del texto al que pertence la entidad
    parrafo = models.ForeignKey(Parrafo)

    #Eliminado lógico de un token
    eliminado = models.BooleanField()

    history = HistoricalRecords()


class Mensaje(models.Model):
    """Entidad que almacena mensajes entre un usuario y otro"""

    #Quien envía el mensaje
    emisor = models.ForeignKey(User, related_name="emisor_user")

    #Quien tiene que recibir el mensaje
    receptor = models.ForeignKey(User, related_name="receptor_user")

    #Mensaje 
    mensaje = models.TextField()

    #Documento a eliminar
    documento = models.ForeignKey(Documento)

    #Caso al cual el documento se encuentra asociado
    caso = models.ForeignKey(Caso)

    #Eliminado lógico de un mensaje
    eliminado = models.BooleanField()

    #Fecha en que se creo la nota
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    history = HistoricalRecords()

    def __str__(self):
        """Devuelve una frase representativa del modelo"""
        return self.mensaje

class Nota(models.Model):
    """Entidad que almacena una nota o comentario"""

    #Breve descripcion de que trata la nota
    descripcion = models.CharField(max_length=30)

    #Nota almacenada
    nota = models.TextField()

    #Eliminado lógico de una nota
    eliminado = models.BooleanField()

    #Fecha en que se creo la nota
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    history = HistoricalRecords()

    def __str__(self):
        """Devuelve una frase representativa del modelo"""
        return self.nota

class NotaDocumento(Nota):
    """Entidad que almacena una nota o comentario de un documento"""

    entidad = models.ForeignKey(Documento)

class NotaCaso(Nota):
    """Entidad que almacena una nota o comentario de un documento"""

    entidad = models.ForeignKey(Caso)

class ResultadoHeader(models.Model):
    """Entidad que almacena el header de resultado parcial de búsqueda"""

    #Fecha en la cuál se guardó
    fecha = models.DateTimeField(auto_now_add=True)

    #Caso al que pertence la búsqueda
    caso = models.ForeignKey(Caso)

    #Tipo de búsqueda guardada (general/guiada/inteligente)
    busqueda = models.CharField(max_length=15)

    #Parámetro por el cuál se realizo la búsqueda
    tipo = models.CharField(max_length=15)

    #Estado actual del resultado respecto al caso (True=actualizado/False=no actualizado)
    estado = models.BooleanField()

    #Documentos asociados al caso en el momento exacto en que se hizo la búsqueda
    documentos = models.ManyToManyField(Documento)

    #Usuario que general el resultado
    propietario = models.ForeignKey(User, related_name="propietario_resultado")

    #Eliminado lógico
    eliminado = models.BooleanField()

    history = HistoricalRecords()

class ResultadoBusqGeneral(models.Model):
    """Entidad que almacena la información de cada item de un resultado de búsqueda inteligente"""
    
    #Campo destacado del resultado
    destacado = models.BooleanField()

    #Párrafo en el cuál se encuentra el resultado
    parrafo_nro = models.IntegerField()

    #Posicion en la que se encuentra dentro del párrafo
    posicion = models.IntegerField()

    #Id del documento
    documento = models.ForeignKey(Documento)

    #Nombre del documento
    documento_nombre = models.CharField(max_length=100)

    #Texto del párrafo
    parrafo = models.TextField()

    #Header correspondiente al resultado
    header = models.ForeignKey(ResultadoHeader)

    history = HistoricalRecords()

class ResultadoBusqInteligente(models.Model):
    """Entidad que almacena la información de cada item de un resultado de búsqueda inteligente"""
    
    #Campo destacado del resultado
    destacado = models.BooleanField()

    #Documento en base al cual se ha obtenido la entidad
    doc = models.ForeignKey(Documento)

    #Texto relacionado a la entidad
    string = models.CharField(max_length=50)

    #Texto relacionado a la entidad que ha sido editado
    string_original = models.CharField(max_length=50)

    #Comienzo del string
    start = models.IntegerField()

    #Final del string en cantidad de tokens
    end = models.IntegerField()
    
    #Nro de párrafo
    parrafo_nro = models.IntegerField()

    #Texto del párrafo
    parrafo = models.TextField()

    #Header correspondiente al resultado
    header = models.ForeignKey(ResultadoHeader)

    history = HistoricalRecords()

class ResultadoBusqInteligenteTokens(models.Model):
    """Entidad que almacena la información de cada item de un resultado de búsqueda inteligente"""
    
    #Campo destacado del resultado
    destacado = models.BooleanField()

    #Documento en base al cual se ha obtenido la entidad
    doc = models.ForeignKey(Documento)

    #Aparicion 
    aparicion = models.CharField(max_length=50)

    #Sustantivo/Verbo
    tipo = models.CharField(max_length=10)

    #Frase completa
    frase = models.CharField(max_length=150)

    #Lema en la que se basa la aparición
    lema = models.CharField(max_length=50)

    #Categoría a la que pertenece la palabra detectada
    categoria = models.CharField(max_length=50)

    #Párrafo del texto al que pertence la entidad
    parrafo = models.ForeignKey(Parrafo)

    #Número de párrafo
    parrafo_nro = models.IntegerField()

    #Header correspondiente al resultado
    header = models.ForeignKey(ResultadoHeader)

    history = HistoricalRecords()

class ResultadoBusqGuiadaGeneral(models.Model):
    """Entidad que almacena la información de la clave de cada item de un resultado de búsqueda guiada"""

    #Clave del resultado
    clave = models.CharField(max_length=200)

    #Campo destacado del resultado
    destacado = models.BooleanField()
    
    #Cantidad de apariciones
    cantidadTotal = models.IntegerField()

    #Header correspondiente al resultado
    header = models.ForeignKey(ResultadoHeader)

class ResultadoBusqGuiada(models.Model):
    """Entidad que almacena la información de un item respecto a un documento específico"""
    
    #Id del documento
    documento = models.ForeignKey(Documento)

    #Nombre del documento
    documento_nombre = models.CharField(max_length=100)

    #Comienzo del string
    start = models.IntegerField()

    #Final del string
    end = models.IntegerField()
    
    #Nro de párrafo
    parrafo_nro = models.IntegerField()

    #Texto del párrafo
    parrafo = models.TextField()

    #Búsqueda guiada general correspondiente
    general = models.ForeignKey(ResultadoBusqGuiadaGeneral)

    history = HistoricalRecords()

class Informe(models.Model):
    """Almacena la ubicación de donde se encuentra guardado un informe"""

    #Caso del cual refiere el informe
    caso = models.ForeignKey(Caso)

    #Usuario que general el informe
    propietario = models.ForeignKey(User, related_name="propietario_informe")

    #Tipo de búsqueda guardada (general/guiada/inteligente)
    busqueda = models.CharField(max_length=15)

    #Fecha en la cual se genero el informe
    fecha = models.DateTimeField(auto_now_add=True)

    #Path en el cuál se encuentra el informe
    path = models.CharField(max_length=300, null=True)

    #Eliminado lógico
    eliminado = models.BooleanField()

    history = HistoricalRecords()

    
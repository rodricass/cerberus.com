from .text import LectorDOCX, LectorTXT
from django.http import Http404
from django.http import HttpResponse
from .myclasses import Modelo, ModeloEconomico, ModeloDrogas
import os

#-----------------------------------------------------------------------------------------------------------------------------------------------
# Depende de los tipos de formatos de documentos que soporte, si se agregan nuevos formatos es necesario modificar los diccionarios 'lectores_dict' y 'extension_dict'

class ExtensionArchivo:
    """ Clase para obtener información específica respecto a la extensión de un archivo"""

    def getLector(self,ext,file):
    #Si se agrega un formato de archivo nuevo es necesario agregar aca la referencia a su lector correspondiente y crear la clase correspondiente en 'text.py'
        lectores_dict = {
            "txt":LectorTXT,
            "docx":LectorDOCX,
        }

        if ext in lectores_dict.keys():
            return lectores_dict[ext](file)
        else: 
            raise Http404("Extensión de archivo no soportada")

    def getResponseDoc(self,ext):
        #Si se agrega un formato de archivo nuevo es necesario agregar aca la referencia a su formato de descarga correspondiente
        extension_dict = {
            "txt":'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            "docx":'text/plain',
        }
        if ext in extension_dict.keys():
            return extension_dict[ext]
        else: 
            raise Http404("Extensión de archivo no soportada")

#-----------------------------------------------------------------------------------------------------------------------------------------------
# Depende de los tipos de palabras que soporta el tokenizer, si se agregaran nuevos es necesario modificar el diccionario 'tipo_token'
    
class GetTipoToken:
    """Clase para obtener el tipo de token"""

    #Si se agrega un tipo nuevo de token es necesario agregar su clave y nombre
    tipo_token = {
                    "NOUN":"Sustantivo",
                    "VERB":"Verbo",
                    "ADJ": "Adjetivo",
                 }

    def getTipoToken(self,tipo):
        if tipo in self.tipo_token.keys():
            return self.tipo_token[tipo]
        else: 
            raise Http404("Tipo de token desconocido")

#-----------------------------------------------------------------------------------------------------------------------------------------------
# Depende de las entidades que soporte la búsqueda inteligente, si se agregaran nuevas, es necesario modificar el diccionario 'entidades_dic'

class GetEntidad:
    """Clase para obtener tipo de entidad"""

    #Si se agrega un nuevo tipo de entidad es necesario agregar aca su clave y nombre
    entidades_dic = {
                        "Organizaciones":"ORG",
                        "Locaciones":"LOC",
                        "Personas":"PER",
                        "Búsqueda":"BUS",
                        "Drogas":"DRUG",
                        "Económicos":"ECON",
                    }

    def getEntidad(self,tipo):
        if tipo in self.entidades_dic.keys():
            return self.entidades_dic[tipo]
        else:
            raise Http404("Entidad no existente")

#-----------------------------------------------------------------------------------------------------------------------------------------------
# Depende de los modelos que posea disponibles la librería nlp, si se agregaran nuevos es necesario modificar los diccionarios 'tipos_modelos'

class TipoModelo:
    """ Clase para obtener información específica en base al tipo de modelo"""

    def getModelo(self,tipo):
    #Si se agrega un modelo nuevo es necesario agregar aqui la referencia al modelo respectivo y crear su correspondiente clase en 'myclasses.py'
        
        tipos_modelos = {
            'ECON':ModeloEconomico,
            'DRUG':ModeloDrogas,
            }

    
        if tipo in tipos_modelos.keys():
            return tipos_modelos[tipo]()
        else: 
            raise Http404(f'Modelo {tipo} inexistente')

    def getModelChoices(self):
        #Si se agrega un modelo nuevo es necesario agregar aqui la clave del mismo y la palabra identificatoria
        
        tipos_modelos = {
            'DRUG':'Drogas',
            'ECON':'Económico',
            }

        MODEL_CHOICES = []
        for k, v in tipos_modelos.items():
            MODEL_CHOICES.append((k,v))

        return MODEL_CHOICES

#-----------------------------------------------------------------------------------------------------------------------------------------------
# Debido al formato poco útil que poseen los archivos de WhatsApp generados por UFED, acá se determina la posibilidad de tratar distinto a los archivos comunes y los UFED

class TipoArchivo:
    """ Clase para obtener información específica en base al tipo de archivo, si se agregan nuevos tipos revisar 'fileuploader.py' """

    def getTipoArchivoChoices(self):
        #Si se agrega un formato nuevo de tipo de archivo que desee procesar de manera distinta, agregar al diccionario 'tipos_archivos'

        tipos_archivos = {
            'UFED':'WhatsApp UFED',
            'OTROS':'Archivos comunes',
            }

        TIPO_CHOICES = []
        for k, v in tipos_archivos.items():
            TIPO_CHOICES.append((k,v))

        return TIPO_CHOICES
from .text import LectorDOCX, LectorTXT
from django.http import Http404
from django.http import HttpResponse
from .models import Documento
from .myclasses import Modelo, ModeloEconomico, ModeloDrogas
import os



class ExtensionArchivo:
    """ Clase para obtener información específica respecto a la extensión de un archivo"""

    def getLector(self,ext,file):
    #Si se agrega un formato de archivo nuevo es necesario agregar aca la referencia a su lector correspondiente
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

def model_factory(tipo):
    """Factory de modelos"""

    tipos_modelos = {
            'ECON':ModeloEconomico(),
            'DRUG':ModeloDrogas(),
            }

    return tipos_modelos[tipo]
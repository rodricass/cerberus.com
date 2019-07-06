import re
from django.http import Http404
from nlp_model_gen import NLPModelAdmin

nlp = NLPModelAdmin()

sep_telefonos = r"[ -]"

#class Regex():
#    """Almacena expresiones regulares para poder ser utilizadas en la búsqueda dentro de archivos"""
#    _pattern = ""

#    def __init__(self):
#        """Inicializa la clase"""
#        self.regex = None

#    @property
#    def pattern(self):
#        if self.regex:
#            return self.regex
#        self.regex = re.compile(self._pattern)
#        return self.regex

#    @pattern.setter
#    def pattern(self, other):
#        pass
   

#class RegexEmail(Regex):
#    """Almacena expresion regular de email"""
#    _pattern = r"[^@\s]+@[^@\s]+\.[^@\s]+"

#class RegexUrl(Regex):
#    """Almacena expresion regular de url"""
#    _pattern = r"[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)" # [\s]"

#class RegexTarjeta(Regex):
#    """Almacena expresion regular de tarjetas de credito"""
#    _pattern = r"((\d{4} \d{6} \d{5})|(\d{4} \d{4} \d{4} \d{4}))"
        
#class RegexDocumento(Regex):
#    """Almacena expresion regular de documento de identidad"""
#    _pattern = r"[1-9]{2,3}\.?[0-9]{3}\.?[0-9]{3}"  

#class RegexTelefono(Regex):
#    """Almacena expresion regular de documento de identidad"""
#    _pattern = fr"\+?([0-9]{1,2})?{sep_telefonos}?9?{sep_telefonos}?[0-9 \-]?" + r"[0-9]{6,13}"



class Modelo:
    """Clase padre de modelos"""

    _model = "" 

    def __init__(self):
        pass

    #Analiza texto en base a modelo economico
    def analyze(self,text):
        task = nlp.analyze_text(self._model, text, True) 
        if task['success']:
            return task['resource']['task_id']
        else:
            raise Http404("Error al procesar la solicitud")
    
    #Determina si el análisis concluyó o no
    def is_analysis_ready(self, id):
        task_status = nlp.get_task_status(id)
        if task_status['success']:
            if task_status['resource']['error']['active']:
                raise Http404("Error de análisis de texto")
            return task_status['resource']['status'] == 'finished'
      
    #Retorna los resultados de un análisis
    def get_task_results(self, id):
        task_status = nlp.get_task_status(id)
        return task_status['resource']['results']

    @property
    def model(self):
        return self._model


class ModeloEconomico(Modelo):
    """Carga modelo economico"""

    _model = "modelo_economico"

    

class ModeloDrogas(Modelo):
    """Carga modelo drogas"""

    _model = "modelo_drogas"
    


"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from .models import Investigacion, Documento, Nota, ResultadoHeader, Regex

class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'Usuario'}),
                               label='')
    password = forms.CharField(label='',
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Contraseña',}))

class InvestigacionForm(forms.ModelForm):
    """Forma para completar la información correspondiente a las investigaciones"""
    class Meta:
        model = Investigacion
        fields = ['identificador','nombre','descripcion','modelo']
        labels = {'nombre':'','identificador':'','descripcion':'','modelo':'Modelo',}
        widgets = {'nombre': forms.TextInput({'placeholder':'Nombre de la investigación'}),
                   'identificador': forms.TextInput({'placeholder':'Identificador de la investigación'}),
                   'descripcion': forms.Textarea({'placeholder':'Descripción de la investigación'})}

class DocumentoForm(forms.ModelForm):
    """Forma para completar la información correspondiente a los documentos"""
    class Meta:
        model = Documento
        fields = ['tipo_archivo','documento']
        labels = {'documento':'','tipo_archivo':''}
        widgets = {'documento':forms.ClearableFileInput({'accept':'.txt,.docx','class':'documentos','multiple':True})}

class InvestigacionFormEdit(forms.ModelForm):
    """Forma para completar la información correspondiente a las investigaciones"""
    class Meta:
        model = Investigacion
        fields = ['identificador','nombre','descripcion']
        widgets = {'nombre': forms.TextInput({'placeholder':'Nombre de la investigación'}),
                   'identificador': forms.TextInput({'placeholder':'Identificador de la investigación'}),
                   'descripcion': forms.Textarea({'placeholder':'Descripción de la investigación'})}

class BuscadorGeneralForm(forms.Form):
    """Forma para completar con alguna frase a buscar dentro de los archivos de una investigacion"""
    busqueda = forms.CharField(label='',
                               widget=forms.Textarea({
                                   'placeholder':'Inserte texto a buscar'}))

class BuscadorInvestigacionesForm(forms.Form):
    """Forma para mostrar los investigaciones del usuario"""
    def __init__(self, user, *args, **kwargs):
        super(BuscadorInvestigacionesForm, self).__init__(*args, **kwargs)
        investigaciones = Investigacion.objects.filter(usuario=user).filter(eliminado=False).filter(finalizado_correcto=False).filter(finalizado_incorrecto=False).order_by('-fecha_agregado')
        self.fields['investigaciones'] = forms.ChoiceField(label='', choices=[(investigacion.id,investigacion.nombre if len(investigacion.nombre)<73 else f'{investigacion.nombre[:73]}..') for investigacion in investigaciones])

class UsuariosForm(forms.Form):
    """Forma para mostrar los investigaciones del usuario"""
    def __init__(self, user, *args, **kwargs):
        super(UsuariosForm, self).__init__(*args, **kwargs)
        usuarios = User.objects.exclude(id=user.id)
        self.fields['usuarios'] = forms.ChoiceField(label='', choices=[(usuario.id,usuario.username) for usuario in usuarios])

class NotaForm(forms.ModelForm):
    """Forma para crear notas"""
    class Meta:
        model = Nota
        fields = ['descripcion','nota']
        labels = {'descripcion':'', 'nota':''}
        widgets = {'descripcion': forms.TextInput({'placeholder':'Asunto'}),
                   'nota': forms.Textarea({'placeholder':'Nota'})}

class UsuarioNuevoForm(forms.Form):
    """Forma para crear usuarios nuevos"""
    nombre = forms.CharField(label='',
                               widget=forms.TextInput({
                                   'placeholder':'Nombre de usuario'}))
    contraseña = forms.CharField(label='',
                                    widget=forms.PasswordInput({
                                   'placeholder':'Contraseña'}))


class RegexForm(forms.ModelForm):
    """Forma para crear expresiones regulares"""
    class Meta:
        model = Regex
        fields = ['nombre','patron','orden']
        labels = {'nombre':'', 'patron':'', 'orden':''}
        widgets = {'nombre': forms.TextInput({'placeholder':'Nombre'}),
                   'patron': forms.TextInput({'placeholder':'Patrón'}),
                   'orden': forms.NumberInput({'placeholder':'Orden'})}
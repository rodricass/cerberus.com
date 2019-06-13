"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from .models import Caso, Documento, Nota, ResultadoHeader

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

class CasoForm(forms.ModelForm):
    """Forma para completar la información correspondiente a los casos"""
    class Meta:
        model = Caso
        fields = ['identificador','nombre','descripcion','modelo']
        labels = {'nombre':'','identificador':'','descripcion':'','modelo':'Modelo',}
        widgets = {'nombre': forms.TextInput({'placeholder':'Nombre del caso'}),
                   'identificador': forms.TextInput({'placeholder':'Identificador del caso'}),
                   'descripcion': forms.Textarea({'placeholder':'Descripción del caso'})}

class DocumentoForm(forms.ModelForm):
    """Forma para completar la información correspondiente a los documentos"""
    class Meta:
        model = Documento
        fields = ['documento']
        labels = {'documento':''}
        widgets = {'documento':forms.ClearableFileInput({'accept':'.txt,.docx','class':'documentos','multiple':True})}

        #'nombre_doc':forms.HiddenInput({'class':'nombres'}),
        #           'titulo':forms.TextInput({'placeholder':'Nombre del documento',
        #                                     'class':'nombres'}),
        #           'descripcion_doc':forms.Textarea({'placeholder':'Descripción del documento (opcional)'}),

class CasoFormEdit(forms.ModelForm):
    """Forma para completar la información correspondiente a los casos"""
    class Meta:
        model = Caso
        fields = ['identificador','nombre','descripcion']
        widgets = {'nombre': forms.TextInput({'placeholder':'Nombre del caso'}),
                   'identificador': forms.TextInput({'placeholder':'Identificador del caso'}),
                   'descripcion': forms.Textarea({'placeholder':'Descripción del caso'})}

class BuscadorGeneralForm(forms.Form):
    """Forma para completar con alguna frase a buscar dentro de los archivos de un caso"""
    busqueda = forms.CharField(label='',
                               widget=forms.Textarea({
                                   'placeholder':'Inserte texto a buscar'}))

class BuscadorCasosForm(forms.Form):
    """Forma para mostrar los casos del usuario"""
    def __init__(self, user, *args, **kwargs):
        super(BuscadorCasosForm, self).__init__(*args, **kwargs)
        casos = Caso.objects.filter(usuario=user).filter(eliminado=False).filter(finalizado_correcto=False).filter(finalizado_incorrecto=False).order_by('-fecha_agregado')
        self.fields['casos'] = forms.ChoiceField(label='', choices=[(caso.id,caso.nombre) for caso in casos])

class UsuariosForm(forms.Form):
    """Forma para mostrar los casos del usuario"""
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


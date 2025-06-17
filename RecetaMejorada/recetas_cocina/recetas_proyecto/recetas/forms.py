# recetas/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Receta, Ingrediente, RecetaIngrediente, Usuario
# Asegúrate de importar inlineformset_factory
from django.forms import inlineformset_factory
# Importa FormHelper y Layout
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, HTML

class FormularioRegistroUsuario(UserCreationForm):
    nombre_usuario = forms.CharField(max_length=100)
    email = forms.EmailField()

    class Meta:
        model = User
        # Asegúrate de que estos campos existan o se manejen en tu modelo User extendido
        # password1 y password2 son inherentes de UserCreationForm, no los pongas en 'fields' de Meta si no quieres duplicidad
        fields = ('username', 'email') # Elimino 'nombre_usuario' aquí porque ya está como campo directo del formulario
        # Nota: UserCreationForm ya maneja las contraseñas. 'nombre_usuario' y 'email' deben ser manejados en save() de la vista o en tu modelo Usuario.

    # Si Usuario tiene OneToOne con User y copia campos, la lógica de guardado debe estar en la vista.
    # Por ejemplo, en tu vista registro_usuario, creas Usuario.objects.create(user=user, ...)
    # El campo 'nombre_usuario' en FormularioRegistroUsuario NO ES el campo 'username' del modelo User.
    # Si quieres que 'nombre_usuario' del modelo Usuario se llene con el 'username' del formulario,
    # simplemente guarda el user, y luego crea el Usuario pasándole user.username al campo nombre_usuario.
    # O mejor aún, haz que 'nombre_usuario' en el modelo Usuario sea opcional o derive del user.username.

class FormularioReceta(forms.ModelForm):
    class Meta:
        model = Receta
        fields = ['nombre', 'descripcion', 'categoria', 'imagen']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
            # --- CAMBIO IMPORTANTE AQUÍ ---
            # Si 'imagen' es ImageField en models.py y quieres subir archivos,
            # DEBES ELIMINAR el widget TextInput. Django usará el widget FileInput por defecto.
            # Si NO quieres subir archivos y solo pegar URLs, entonces tu modelo 'imagen' debería ser CharField o URLField.
            # Asumo que quieres subir archivos, así que lo elimino.
            # 'imagen': forms.TextInput(attrs={'placeholder': 'URLs de la imagen'})
        }
class FormularioIngrediente(forms.ModelForm):
    class Meta:
        model = Ingrediente
        fields = ['nombre']
class RecetaForm(forms.ModelForm):
    class Meta:
        model = Receta
        fields = ['nombre', 'descripcion', 'categoria', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la receta'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descripción de la receta'
            }),
            'categoria': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Categoría'
            }),
            'imagen': forms.FileInput(attrs={
                'class': 'form-control-file'
            })
        }

class RecetaIngredienteForm(forms.ModelForm):
    class Meta:
        model = RecetaIngrediente
        fields = ['ingrediente', 'cantidad']
        widgets = {
            'ingrediente': forms.Select(attrs={
                'class': 'form-control ingrediente-select'
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ingrediente'].queryset = Ingrediente.objects.all()
        self.fields['ingrediente'].empty_label = "Seleccionar ingrediente"

# Formset para manejar múltiples ingredientes
RecetaIngredienteFormSet = inlineformset_factory(
    Receta, 
    RecetaIngrediente,
    form=RecetaIngredienteForm,
    extra=1,  # Formulario extra vacío
    can_delete=True,
    min_num=1,  # Mínimo un ingrediente
    validate_min=True
)
class FormularioBusqueda(forms.Form):
    ingrediente = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Buscar por ingrediente',
            'class': 'form-control'
        })
    )

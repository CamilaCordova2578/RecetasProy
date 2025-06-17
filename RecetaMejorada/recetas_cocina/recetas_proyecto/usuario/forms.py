# recetas_proyecto/usuario/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm # Importa PasswordChangeForm para la base
from django.contrib.auth import get_user_model # Siempre usa get_user_model()
from django.core.exceptions import ValidationError # Necesario para raise ValidationError

# Importa tu modelo Perfil. Asegúrate de que el nombre aquí coincida con tu models.py
from .models import Perfil # ¡Importante: Si tu modelo es Perfil, usa Perfil aquí!

# Obtén el modelo de usuario activo. Esto es crucial para la flexibilidad.
User = get_user_model()

class FormularioRegistro(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Usuario para iniciar sesión (único)'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com'
        })
        self.fields['first_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Tu nombre'
        })
        self.fields['last_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Tu apellido'
        })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este email ya está registrado.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        
        if commit:
            user.save()
            Perfil.objects.create(usuario=user, descripcion="Hola, soy un nuevo usuario.")
        return user

class FormularioLogin(AuthenticationForm):
    """Formulario personalizado para login"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Usuario o Email' # Puedes permitir login con email también, si tu backend de autenticación lo soporta
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })


class FormularioEditarPerfil(forms.ModelForm):
    """
    Formulario para editar el perfil del usuario.
    Permite editar campos del modelo User (first_name, last_name, email)
    y campos del modelo Perfil.
    """
    # Campos del modelo User que queremos editar junto al perfil
    first_name = forms.CharField(
        max_length=30, required=False, label='Nombre',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu nombre'})
    )
    last_name = forms.CharField(
        max_length=30, required=False, label='Apellido',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu apellido'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'})
    )

    class Meta:
        model = Perfil # ¡Importante: usa tu modelo Perfil!
        fields = [
            'foto_perfil',
            'descripcion',
            'fecha_nacimiento',
            # NO incluyas campos que no están en el modelo Perfil aquí
            # He eliminado los campos que no están en tu modelo Perfil inicial:
            # 'nombre_usuario', 'biografia', 'ubicacion', 'telefono',
            # 'sitio_web', 'es_chef_profesional', 'especialidad_culinaria'
            # Si tu modelo Perfil tiene estos campos, inclúyelos.
            # Basado en tu modelo Perfil: foto_perfil, descripcion, fecha_nacimiento
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Cuéntanos sobre ti...'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'foto_perfil': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        # Es crucial pasar la instancia del Perfil al formulario para que funcione el .instance.
        # Cuando editas un perfil, usualmente se pasa instance=request.user.perfil
        super().__init__(*args, **kwargs)

        # Si el formulario está ligado a una instancia de Perfil existente (self.instance no es None)
        if self.instance and self.instance.usuario: # self.instance es el objeto Perfil
            self.fields['first_name'].initial = self.instance.usuario.first_name
            self.fields['last_name'].initial = self.instance.usuario.last_name
            self.fields['email'].initial = self.instance.usuario.email

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # self.instance es el objeto Perfil al que está ligado el formulario
        # self.instance.usuario es el objeto User asociado a ese Perfil
        user_instance = self.instance.usuario
        if User.objects.filter(email=email).exclude(pk=user_instance.pk).exists():
            raise ValidationError("Este email ya está registrado por otro usuario.")
        return email

    # Elimino clean_nombre_usuario porque no es un campo en tu modelo Perfil ni en este formulario.
    # Si añades 'nombre_usuario' a tu modelo Perfil y al Meta.fields de este formulario,
    # entonces sí podrías reactivar esta función de limpieza.

    def save(self, commit=True):
        perfil = super().save(commit=False) # Guarda los campos del Perfil (pero aún no en DB)
        
        # Actualizar también los campos del modelo User
        # Accede al User asociado a este Perfil
        user = perfil.usuario # CORRECTO: usa perfil.usuario (no perfil.user)
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.email = self.cleaned_data.get('email')
        
        if commit:
            user.save() # Guarda los cambios en el objeto User
            perfil.save() # Guarda los cambios en el objeto Perfil
        return perfil


class FormularioCambiarContrasena(forms.Form):
    """
    Formulario para cambiar la contraseña del usuario.
    No es un ModelForm porque no edita directamente un modelo,
    sino que interactúa con la autenticación de Django.
    """
    contrasena_actual = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña actual'
        }),
        label='Contraseña actual'
    )
    
    nueva_contrasena = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nueva contraseña'
        }),
        label='Nueva contraseña',
        min_length=8, # Puedes ajustar la longitud mínima según tus requisitos de seguridad
        help_text='Mínimo 8 caracteres. Debe incluir letras mayúsculas, minúsculas, números y símbolos.'
    )
    
    confirmar_contrasena = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar nueva contraseña'
        }),
        label='Confirmar nueva contraseña'
    )

    def __init__(self, user, *args, **kwargs):
        # Es crucial pasar la instancia del usuario a este formulario
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_contrasena_actual(self):
        contrasena_actual = self.cleaned_data.get('contrasena_actual')
        # Verifica que la contraseña actual sea correcta
        if not self.user.check_password(contrasena_actual):
            raise ValidationError("La contraseña actual es incorrecta.")
        return contrasena_actual

    def clean(self):
        # Esta función de limpieza se ejecuta DESPUÉS de las clean_campo individual.
        # Aquí verificamos que las nuevas contraseñas coincidan.
        cleaned_data = super().clean()
        nueva_contrasena = cleaned_data.get('nueva_contrasena')
        confirmar_contrasena = cleaned_data.get('confirmar_contrasena')

        if nueva_contrasena and confirmar_contrasena: # Si ambos campos tienen valor
            if nueva_contrasena != confirmar_contrasena:
                raise ValidationError("Las nuevas contraseñas no coinciden.")
        
        # Opcional: Puedes añadir validaciones de complejidad aquí,
        # o usar Django's PasswordValidator en settings.py.
        # if not any(char.isdigit() for char in nueva_contrasena):
        #     self.add_error('nueva_contrasena', 'La contraseña debe contener al menos un número.')
        # if not any(char.isupper() for char in nueva_contrasena):
        #     self.add_error('nueva_contrasena', 'La contraseña debe contener al menos una letra mayúscula.')
        
        return cleaned_data

    def save(self):
        # Cambia la contraseña del usuario y la guarda.
        nueva_contrasena = self.cleaned_data['nueva_contrasena']
        self.user.set_password(nueva_contrasena) # Encripta la nueva contraseña
        self.user.save() # Guarda el usuario con la nueva contraseña
        return self.user

# Puedes añadir más formularios aquí si los necesitas, como un FormularioEliminarCuenta, etc.
# Si en tus vistas necesitas un formulario para "Configuración de Cuenta", y este incluye
# campos que no son de Perfil ni de Contraseña, tendrías que crear uno nuevo.
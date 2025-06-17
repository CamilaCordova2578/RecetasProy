# usuarios/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
# Asegúrate de importar tu modelo Perfil, no PerfilUsuario
from .models import Perfil # <--- CAMBIO AQUÍ: Importa tu modelo Perfil

# Clase Inline para el Perfil, para que aparezca al editar un Usuario
class PerfilInline(admin.StackedInline): # <--- CAMBIO AQUÍ: Nombre de la clase
    model = Perfil # <--- CAMBIO AQUÍ: Usa tu modelo Perfil
    can_delete = False # No permitir eliminar el perfil desde el inline del usuario
    verbose_name_plural = 'Perfil de Usuario' # Etiqueta en el panel de administración

    # Los campos que tu modelo Perfil SÍ tiene
    fields = (
        'foto_perfil',
        'descripcion', # Tu campo es 'descripcion', no 'biografia'
        'fecha_nacimiento',
    )
    # Si quieres campos de solo lectura, añádelos aquí:
    # readonly_fields = ('algun_campo_de_solo_lectura',)


# Clase de administración para el modelo User de Django
class UserAdmin(BaseUserAdmin):
    inlines = (PerfilInline,) # <--- CAMBIO AQUÍ: Usa tu PerfilInline

    # Columnas a mostrar en la lista de usuarios.
    # Quitamos los campos que no existen en el modelo Perfil simplificado.
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'is_active', # Es mejor mostrar si el usuario está activo (viene de User)
        'is_staff',
        'get_descripcion_corta', # Nuevo método para la descripción
        'get_fecha_nacimiento_perfil', # Nuevo método para la fecha de nacimiento
    )

    # Filtros que se muestran en la barra lateral derecha.
    # Adaptamos a los campos que realmente existen en tu modelo Perfil.
    list_filter = BaseUserAdmin.list_filter + (
        # 'perfil__es_chef_profesional', # Este campo NO existe en tu modelo Perfil
        # 'perfil__activo',              # Este campo NO existe en tu modelo Perfil
        # Puedes añadir filtros basados en los campos de tu modelo Perfil si son interesantes
        # Por ejemplo:
        # 'perfil__fecha_nacimiento',
    )

    # Métodos personalizados para mostrar datos del perfil en la lista de usuarios
    def get_descripcion_corta(self, obj):
        # Asegúrate de que el perfil exista antes de intentar acceder a él
        if hasattr(obj, 'perfil') and obj.perfil.descripcion:
            # Mostrar solo una parte de la descripción si es muy larga
            return obj.perfil.descripcion[:50] + '...' if len(obj.perfil.descripcion) > 50 else obj.perfil.descripcion
        return '-'
    get_descripcion_corta.short_description = 'Descripción de Perfil'

    def get_fecha_nacimiento_perfil(self, obj):
        if hasattr(obj, 'perfil') and obj.perfil.fecha_nacimiento:
            return obj.perfil.fecha_nacimiento
        return '-'
    get_fecha_nacimiento_perfil.short_description = 'Fecha Nacimiento'


# Clase de administración para el propio modelo Perfil (para gestionar perfiles directamente)
# Si no necesitas gestionar Perfiles por separado y solo a través del User, puedes omitir esta parte.
# Pero generalmente es útil tenerla.
@admin.register(Perfil) # <--- CAMBIO AQUÍ: Registra tu modelo Perfil
class PerfilAdmin(admin.ModelAdmin): # <--- CAMBIO AQUÍ: Nombre de la clase
    # Columnas a mostrar cuando ves la lista de perfiles
    list_display = (
        'usuario_username', # Método para obtener el username del usuario relacionado
        'get_nombre_completo_usuario', # Método para obtener nombre completo del User
        'descripcion', # Tu campo es 'descripcion'
        'fecha_nacimiento',
        'foto_perfil_thumbnail', # Método para mostrar una miniatura de la foto
        # Quitamos campos que no existen: 'nombre_usuario', 'email', 'es_chef_profesional', 'activo', 'fecha_registro'
    )

    # Filtros para la lista de perfiles
    list_filter = (
        # 'fecha_registro', # Este campo NO existe en tu modelo Perfil
        'fecha_nacimiento',
    )

    # Campos por los que se puede buscar
    search_fields = (
        'usuario__username', # Busca por el username del User relacionado
        'usuario__first_name',
        'usuario__last_name',
        'descripcion',
    )

    # Campos de solo lectura
    readonly_fields = (
        # 'fecha_registro', 'fecha_actualizacion', # Estos campos NO existen en tu modelo Perfil
    )

    # Agrupación de campos en el formulario de edición de perfil
    fieldsets = (
        ('Información Básica del Perfil', {
            'fields': ('usuario', 'foto_perfil', 'descripcion', 'fecha_nacimiento',)
        }),
        # Quitamos las secciones de Información Personal extendida e Información Culinaria si los campos no existen
        # ('Información Personal', {
        #     'fields': ('ubicacion', 'telefono', 'sitio_web')
        # }),
        # ('Información Culinaria', {
        #     'fields': ('es_chef_profesional', 'especialidad_culinaria')
        # }),
        # ('Estado y Fechas', {
        #     'fields': ('activo', 'fecha_registro', 'fecha_actualizacion'),
        #     'classes': ('collapse',)
        # }),
    )

    # Métodos auxiliares para PerfilAdmin
    def usuario_username(self, obj):
        return obj.usuario.username
    usuario_username.short_description = 'Usuario (Login)'
    usuario_username.admin_order_field = 'usuario__username' # Permite ordenar por este campo

    def get_nombre_completo_usuario(self, obj):
        return f"{obj.usuario.first_name} {obj.usuario.last_name}" if obj.usuario.first_name or obj.usuario.last_name else obj.usuario.username
    get_nombre_completo_usuario.short_description = 'Nombre Completo User'

    def foto_perfil_thumbnail(self, obj):
        from django.utils.html import mark_safe
        if obj.foto_perfil:
            return mark_safe(f'<img src="{obj.foto_perfil.url}" width="50" height="50" style="border-radius: 50%;" />')
        return '-'
    foto_perfil_thumbnail.short_description = 'Miniatura'


# Re-registrar UserAdmin para usar nuestra versión personalizada
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

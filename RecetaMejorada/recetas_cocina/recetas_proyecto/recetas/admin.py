from django.contrib import admin
from .models import Usuario, Receta, Ingrediente, RecetaIngrediente, Favorito

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['nombre_usuario', 'email']

@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'creado_por', 'fecha_creacion']
    list_filter = ['categoria', 'fecha_creacion']

@admin.register(Ingrediente)
class IngredienteAdmin(admin.ModelAdmin):
    list_display = ['nombre']

@admin.register(RecetaIngrediente)
class RecetaIngredienteAdmin(admin.ModelAdmin):
    list_display = ['receta', 'ingrediente', 'cantidad']

@admin.register(Favorito)
class FavoritoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'receta', 'fecha']
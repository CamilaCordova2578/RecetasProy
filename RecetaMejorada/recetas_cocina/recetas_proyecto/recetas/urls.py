# urls.py
from django.urls import path
# Importa las vistas de autenticación de Django si las usas directamente en urls.py
from django.contrib.auth import views as auth_views
from . import views # Asegúrate de que este import es correcto y apunta a tus vistas


urlpatterns = [
    # Rutas de navegación principales
    path('', views.inicio, name='inicio'),
    path('registro/', views.registro_usuario, name='registro'),
    path('login/', auth_views.LoginView.as_view(template_name='recetas/login.html'), name='login'),
    # Asegúrate de que 'inicio' sea una URL válida para la redirección después del logout
    path('logout/', auth_views.LogoutView.as_view(next_page='inicio'), name='logout'),
    path('recetas/', views.lista_recetas, name='lista_recetas'),
    # Nota: Tu template 'perfil_usuario.html' apunta a 'detalle_receta' con 'receta.id'
    # Así que esta URL debe seguir el patrón '<int:receta_id>/'
    path('recetas/<int:receta_id>/', views.detalle_receta, name='detalle_receta'),

    # ---- URL PRINCIPAL PARA EL PERFIL DEL USUARIO ----
    # Esta es la URL que contendrá la lógica para:
    # 1. Mostrar las recetas del usuario.
    # 2. Procesar la creación de nuevas recetas (cuando el formulario POST de crear_receta se envía aquí).
    # 3. Procesar la eliminación de recetas existentes (cuando el formulario POST de eliminar_receta se envía aquí).
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),

    # ---- URL PARA EDITAR UNA RECETA ESPECÍFICA ----
    # Se mantiene como una URL separada para la vista de edición detallada.
    path('recetas/<int:receta_id>/editar/', views.editar_receta, name='editar_receta'),

    # ---- URLs ELIMINADAS/COMENTADAS ----
    # Las siguientes URLs ya NO son necesarias porque su lógica ha sido
    # integrada en la vista 'perfil_usuario'.
    # Si las mantienes, Django intentará mapear a funciones de vista que ya no existen,
    # causando errores.
    path('recetas/crear/', views.crear_receta, name='crear_receta'),
    # path('recetas/<int:receta_id>/eliminar/', views.eliminar_receta, name='eliminar_receta'),

    # ---- Otras URLs que ya tenías y que son correctas ----
    path('recetas/<int:receta_id>/favorito/', views.toggle_favorito, name='toggle_favorito'),
    path('favoritos/', views.mis_favoritos, name='mis_favoritos'),
    path('quitar_favorito/<int:receta_id>/', views.quitar_favorito, name='quitar_favorito'),
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('ingredientes/', views.lista_ingredientes, name='lista_ingredientes'),
    path('ingredientes/crear/', views.crear_ingrediente, name='crear_ingrediente'),
    path('receta/<int:receta_id>/editar/', views.editar_receta, name='editar_receta'),
    path('ajax/agregar-ingrediente/', views.agregar_ingrediente_ajax, name='agregar_ingrediente_ajax'),
    path('receta/<int:receta_id>/eliminar-ingrediente/<int:ingrediente_id>/', 
         views.eliminar_ingrediente_receta, name='eliminar_ingrediente_receta'),
    
    
    path('buscar/', views.buscador_global, name='buscador_global'),
    path('ajax/sugerencias/', views.sugerencias_ajax, name='sugerencias_ajax'),
    
]
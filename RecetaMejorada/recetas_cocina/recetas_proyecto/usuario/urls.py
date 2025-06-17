from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'usuario' # <--- Tu app_name es 'usuarios', no 'usuario'

urlpatterns = [
    # Autenticación
    path('registro/', views.registro_usuario, name='registro'),
    path('login/', views.login_usuario, name='login'), # Tu vista personalizada
    path('logout/', views.logout_usuario, name='logout'), # Tu vista personalizada

    # Perfil personal
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    path('perfil/cambiar-contrasena/', views.cambiar_contrasena, name='cambiar_contrasena'),
    path('perfil/configuracion/', views.configuracion_cuenta, name='configuracion'),
    path('perfil/desactivar/', views.desactivar_cuenta, name='desactivar_cuenta'),

    # Perfiles públicos
    path('usuario/<str:username>/', views.perfil_publico, name='perfil_publico'),
    path('lista/', views.lista_usuarios, name='lista_usuarios'), # Cambiado de 'usuarios/' a 'lista/' para evitar conflicto con el prefijo principal

    # AJAX
    path('ajax/verificar-usuario/', views.ajax_verificar_usuario, name='ajax_verificar_usuario'),
    
    #Recetas del usuario 
    path('mi-perfil/', views.mi_perfil_con_gestion_recetas, name='mi_perfil_con_gestion_recetas'),
]
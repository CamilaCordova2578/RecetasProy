from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
# IMPORTANTE: Cambia 'PerfilUsuario' a 'Perfil'
from .models import Perfil # <--- CAMBIO AQUÍ

from recetas.forms import FormularioReceta # ¡Importante!


from .forms import (
    FormularioRegistro,
    FormularioLogin,
    FormularioEditarPerfil,
    FormularioCambiarContrasena
)
from .models import Perfil # Tu modelo Perfil

# Importa tus modelos de la aplicación 'recetas'
from recetas.models import Receta, RecetaIngrediente, Ingrediente # ¡Importa todos estos!

def perfil_publico(request, username):
    """
    Vista para mostrar el perfil público de un usuario, incluyendo sus recetas y sus ingredientes.
    """
    # 1. Obtener el objeto User de Django.
    user_obj = get_object_or_404(User, username=username, is_active=True)

    # 2. Acceder al objeto Perfil asociado a ese User.
    perfil = user_obj.perfil

    # 3. Obtener las recetas publicadas por este usuario y PRECARGAR sus ingredientes relacionados.
    #    'creado_por' es el nombre de tu ForeignKey en el modelo Receta.
    #    'recetaingrediente_set' es el related_name inverso de Receta a RecetaIngrediente.
    #    'ingrediente' es el campo ForeignKey de RecetaIngrediente a Ingrediente.
    recetas_del_usuario = Receta.objects.filter(creado_por=user_obj).order_by('-fecha_creacion').prefetch_related(
        'recetaingrediente_set__ingrediente'
    )
    # NOTA: Si tuvieras un campo 'publicada=True' en Receta, iría así:
    # recetas_del_usuario = Receta.objects.filter(creado_por=user_obj, publicada=True).order_by('-fecha_creacion').prefetch_related(
    #     'recetaingrediente_set__ingrediente'
    # )


    context = {
        'perfil': perfil,
        'es_perfil_propio': request.user.is_authenticated and perfil.usuario == request.user,
        # Pasar las recetas del usuario (con sus ingredientes precargados) al contexto
        'recetas_usuario': recetas_del_usuario,
    }

    return render(request, 'usuario/perfil_publico.html', context)

def registro_usuario(request):
    if request.user.is_authenticated:
        return redirect('usuario:perfil')

    if request.method == 'POST':
        form = FormularioRegistro(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    login(request, user)
                    messages.success(request, f'¡Bienvenido {user.username}! Tu cuenta ha sido creada exitosamente.')
                    return redirect('usuario:perfil_usuario')
            except Exception as e:
                messages.error(request, f'Error al crear la cuenta: {str(e)}')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = FormularioRegistro()

    return render(request, 'usuario/registro.html', {'form': form})

def login_usuario(request):
    """Vista para iniciar sesión"""
    if request.user.is_authenticated:
        return redirect('usuario:perfil')

    if request.method == 'POST':
        form = FormularioLogin(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Usar user.username si Perfil no tiene nombre_usuario para mensajes.
                messages.success(request, f'¡Bienvenido de vuelta, {user.username}!')

                # Redirigir a la página que intentaba acceder o al perfil
                next_page = request.GET.get('next')
                if next_page:
                    return redirect(next_page)
                #return redirect('usuario:perfil_usuario')
                return redirect('inicio')
            else: # Este else se ejecuta si authenticate devuelve None
                messages.error(request, 'Usuario o contraseña incorrectos.')
        else: # Este else se ejecuta si form.is_valid() es False (errores de validación del formulario)
            messages.error(request, 'Usuario o contraseña incorrectos.') # El error ya lo maneja AuthenticationForm

    else:
        form = FormularioLogin()

    return render(request, 'usuario/login.html', {'form': form})

@login_required
def logout_usuario(request):
    """Vista para cerrar sesión"""
    # Usar user.username si Perfil no tiene nombre_usuario para el mensaje
    nombre_usuario = request.user.username
    logout(request)
    messages.success(request, f'¡Hasta luego, {nombre_usuario}!')
    return redirect('usuario:login')



@login_required
def perfil_usuario(request):
    """Vista unificada para mostrar el perfil del usuario con gestión de sus recetas"""
    usuario_actual = request.user
    # Obtener o crear el perfil del usuario actual          
    perfil, created = Perfil.objects.get_or_create(usuario=usuario_actual)
    # Obtener recetas del usuario actual
    recetas_del_usuario = Receta.objects.filter(creado_por=usuario_actual)\
        .order_by('-fecha_creacion')\
        .prefetch_related('recetaingrediente_set__ingrediente')

    # Depuración: imprimir recetas en consola
    print(f"Usuario actual: {usuario_actual.username} (ID: {usuario_actual.id})")
    print(f"Recetas encontradas: {recetas_del_usuario.count()}")
    for receta in recetas_del_usuario:
        print(f" - {receta.nombre} (creado por {receta.creado_por.username})")

    # Lógica para eliminar una receta
    if request.method == 'POST' and 'eliminar_receta' in request.POST:
        receta_id = request.POST.get('receta_id')
        if receta_id:
            try:
                receta = get_object_or_404(Receta, id=receta_id, creado_por=usuario_actual)
                with transaction.atomic():
                    receta.delete()
                messages.success(request, 'Receta eliminada exitosamente.')
            except Exception as e:
                messages.error(request, f'Error al eliminar la receta: {e}')
        return redirect('usuario:perfil_usuario')  # <- asegurarse que el namespace esté bien

    context = {
        'perfil': perfil,
        'usuario': usuario_actual,
        'recetas_del_usuario': recetas_del_usuario,
        'es_perfil_propio': True,  # Por si lo usas en el template
    }

    return render(request, 'usuario/perfil.html', context)

@login_required
def mi_perfil_con_gestion_recetas(request):
    """
    Vista para el perfil del usuario logueado,
    mostrando información personal y gestionando sus recetas publicadas (ver/editar/eliminar).
    """
    usuario_actual = request.user
    perfil, created = Perfil.objects.get_or_create(usuario=usuario_actual)

    # Obtener las recetas publicadas por el usuario actual (con prefetch para ingredientes)
    recetas_del_usuario = Receta.objects.filter(creado_por=usuario_actual).order_by('-fecha_creacion').prefetch_related(
        'recetaingrediente_set__ingrediente'
    )
    # >>> AÑADE ESTOS PRINTS PARA DEPURAR <<<
    print(f"Usuario actual: {usuario_actual.username} (ID: {usuario_actual.id})")
    print(f"Recetas encontradas para {usuario_actual.username}: {recetas_del_usuario.count()}")
    for receta in recetas_del_usuario:
        print(f" - Receta: {receta.nombre}, Creado por: {receta.creado_por.username}")
    # <<< FIN DE LOS PRINTS PARA DEPURAR >>>

    # Lógica para ELIMINAR una receta existente (esto se mantiene)
    if request.method == 'POST' and 'eliminar_receta' in request.POST:
        receta_id_a_eliminar = request.POST.get('receta_id')
        if receta_id_a_eliminar:
            try:
                receta = get_object_or_404(Receta, id=receta_id_a_eliminar, creado_por=usuario_actual)
                with transaction.atomic():
                    receta.delete()
                messages.success(request, 'Receta eliminada exitosamente.')
            except Exception as e:
                messages.error(request, f'Error al eliminar la receta: {e}')
        return redirect('usuarios:mi_perfil_con_gestion_recetas')

    context = {
        'perfil': perfil,
        'recetas_del_usuario': recetas_del_usuario,
        'es_perfil_propio': True,
    }
    return render(request, 'usuarios/perfil.html', context)
@login_required
def editar_perfil(request):
    """Vista para editar el perfil del usuario"""
    # Accede al perfil usando el related_name "perfil"
    perfil = request.user.perfil

    if request.method == 'POST':
        # Pasar request.FILES para manejar la subida de la foto de perfil
        # Asegúrate de pasar 'user=request.user' a FormularioEditarPerfil si su __init__ lo espera.
        form = FormularioEditarPerfil(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                    messages.success(request, 'Tu perfil ha sido actualizado exitosamente.')
                    return redirect('usuario:perfil_usuario')
            except Exception as e:
                messages.error(request, f'Error al actualizar el perfil: {str(e)}')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = FormularioEditarPerfil(instance=perfil)

    return render(request, 'usuario/editar_perfil.html', {
        'form': form,
        'perfil': perfil
    })

@login_required
def cambiar_contrasena(request):
    """Vista para cambiar la contraseña del usuario"""
    if request.method == 'POST':
        form = FormularioCambiarContrasena(request.user, request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Tu contraseña ha sido cambiada exitosamente.')
                # Actualizar la sesión para que el usuario no tenga que volver a loguearse
                # Si la contraseña ha cambiado, la sesión puede invalidarse.
                # Es buena práctica re-autenticar o redirigir al login.
                # Para simplificar, podrías redirigir al perfil sin re-autenticar en muchos casos.
                # Opcional: update_session_auth_hash(request, request.user) si no quieres desloguear.
                return redirect('usuario:perfil_usuario')
            except Exception as e:
                messages.error(request, f'Error al cambiar la contraseña: {str(e)}')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = FormularioCambiarContrasena(request.user)

    return render(request, 'usuario/cambiar_contrasena.html', {'form': form})


# NOTA: Las siguientes vistas ('configuracion_cuenta', 'desactivar_cuenta',
# 'perfil_publico', 'lista_usuarios', 'ajax_verificar_usuario')
# asumen campos como 'activo' o 'nombre_usuario' en el modelo PerfilUsuario.
# Si tu modelo se llama 'Perfil' y no tiene esos campos, DEBERÁS MODIFICARLAS.
# Te dejo las modificaciones más obvias para PerfilUsuario -> Perfil, pero
# si los campos no existen, estas vistas NO FUNCIONARÁN.

@login_required
def configuracion_cuenta(request):
    """Vista para configuraciones adicionales de la cuenta"""
    perfil = request.user.perfil # <--- CAMBIO: PerfilUsuario a perfil
    
    context = {
        'perfil': perfil,
        'usuario': request.user,
    }
    
    return render(request, 'usuario/configuracion.html', context)

@login_required
@require_http_methods(["POST"])
def desactivar_cuenta(request):
    """Vista para desactivar la cuenta del usuario"""
    if request.method == 'POST':
        confirmacion = request.POST.get('confirmacion')
        if confirmacion == 'DESACTIVAR':
            try:
                with transaction.atomic():
                    # ASUNCIÓN: Tu modelo Perfil NECESITA un campo 'activo = models.BooleanField(default=True)'
                    # Si no lo tiene, esta línea fallará.
                    perfil = request.user.perfil # <--- CAMBIO: PerfilUsuario a perfil
                    # perfil.activo = False # Esta línea requiere el campo 'activo' en tu modelo Perfil
                    # perfil.save()

                    # Esto es la forma estándar de "desactivar" un usuario en Django.
                    request.user.is_active = False
                    request.user.save()

                    logout(request)
                    messages.success(request, 'Tu cuenta ha sido desactivada exitosamente.')
                    return redirect('usuario:login')
            except Exception as e:
                messages.error(request, f'Error al desactivar la cuenta: {str(e)}')
        else:
            messages.error(request, 'Confirmación incorrecta.')
    
    return redirect('usuario:configuracion')


# Si quieres que esta vista solo sea accesible para usuarios logueados, usa el decorador:
@login_required
def lista_usuarios(request):
    """Vista para mostrar una lista de usuarios públicos, excluyendo al usuario logueado."""

    usuario_actual = request.user # Obtenemos el usuario actualmente logueado

    # Recuperar todos los usuarios activos que tienen un perfil,
    # y EXCLUIR el usuario actualmente logueado.
    # Usamos __isnull=False para asegurar que solo consideramos usuarios con un Perfil.
    # Y luego .exclude(id=usuario_actual.id) para excluir al usuario actual por su ID.
    usuarios_a_mostrar = User.objects.filter(
        is_active=True,
        perfil__isnull=False # Asegura que el usuario tenga un perfil asociado
    ).exclude(
        id=usuario_actual.id # Excluye al usuario actual por su ID
    ).order_by('username')

    # Paginación
    paginator = Paginator(usuarios_a_mostrar, 12)  # 12 usuarios por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'usuarios': page_obj, # Ahora 'usuarios' son objetos User, filtrados
        'page_obj': page_obj,
    }

    return render(request, 'usuario/lista_usuarios.html', context)

@login_required
def ajax_verificar_usuario(request):
    """Vista AJAX para verificar si un nombre de usuario de Perfil está disponible"""
    if request.method == 'GET':
        nombre_usuario_a_verificar = request.GET.get('nombre_usuario')
        if nombre_usuario_a_verificar:
            # Dado que tu modelo Perfil simple NO tiene 'nombre_usuario'
            # (solo tiene 'descripcion', 'foto_perfil', 'fecha_nacimiento'),
            # esta verificación debería ser para el 'username' del modelo User.

            # Si quieres verificar la disponibilidad del 'username' del User:
            existe = User.objects.filter(username=nombre_usuario_a_verificar).exclude(pk=request.user.pk).exists()

            # Si insistes en tener un 'nombre_usuario' en Perfil,
            # DEBES AÑADIRLO A TU MODELO PERFIL Y MIGRAR LA DB.
            # Solo entonces esta línea tendría sentido:
            # existe = Perfil.objects.filter(nombre_usuario=nombre_usuario_a_verificar).exclude(usuario=request.user).exists()
            
            return JsonResponse({
                'disponible': not existe,
                'mensaje': 'Nombre de usuario disponible' if not existe else 'Nombre de usuario ya en uso'
            })
    
    return JsonResponse({'error': 'Solicitud inválida'}, status=400)

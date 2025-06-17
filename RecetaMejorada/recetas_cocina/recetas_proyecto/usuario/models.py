from django.db import models
from django.contrib.auth.models import User

class Perfil(models.Model):
    # El related_name="perfil" se añade como un argumento dentro de OneToOneField
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Usuario", related_name="perfil")
    
    foto_perfil = models.ImageField(upload_to='usuarios', null=True, blank=True, verbose_name="Foto de Perfil")
    descripcion = models.CharField(max_length=120, verbose_name="Descripción")
    fecha_nacimiento = models.DateField(null=True, blank=True, verbose_name="Fecha de Nacimiento")

    def __str__(self):
        return str(self.usuario)

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"
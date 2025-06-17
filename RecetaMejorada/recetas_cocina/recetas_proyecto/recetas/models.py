from django.db import models
from django.contrib.auth.models import User

class Usuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre_usuario = models.CharField(max_length=100)
    email = models.EmailField()
    contraseña = models.CharField(max_length=100)  
    
    def __str__(self):
        return self.nombre_usuario

class Ingrediente(models.Model):
    nombre = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nombre

class Receta(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    categoria = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to='recetas/', blank=True, null=True)  
    creado_por = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nombre

class RecetaIngrediente(models.Model):
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE)
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        receta_nombre = self.receta.nombre if self.receta else "Sin receta"
        ingrediente_nombre = self.ingrediente.nombre if self.ingrediente else "Sin ingrediente"
        return f"{receta_nombre} - {ingrediente_nombre}"


class Favorito(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('usuario', 'receta')
    
    def __str__(self):
        return f"{self.usuario.username} - {self.receta.nombre}"
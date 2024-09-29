from django.db import models
from django.contrib.auth.models import User

# Clase para los datos de los negocios
class Negocio(models.Model):
    id_negocio = models.AutoField(primary_key=True)
    logo_negocio = models.ImageField(upload_to='imagenes/', null=True, verbose_name='Logo')
    nombre_negocio = models.CharField(max_length=50, verbose_name='Nombre del Negocio')
    telefono = models.CharField(max_length=50, verbose_name='Teléfono')
    numero_de_local = models.CharField(max_length=50, verbose_name='Dirección')
    correo_de_local = models.CharField(max_length=50, verbose_name='Correo')
    usuario_administrador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='negocios', verbose_name='Usuario Administrador')

    def __str__(self):
        #si queremos mostrar el numero ponemos esto: \n {self.telefono} justo despues de negocio
        return f"{self.nombre_negocio}"

class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    imagen = models.ImageField(upload_to='imagenes/', verbose_name='Imagen', null=True)
    nombre = models.CharField(max_length=50, verbose_name='Nombre')
    precio = models.IntegerField(verbose_name='Precio')
    id_negocio = models.ForeignKey(Negocio, on_delete=models.CASCADE, verbose_name='Id Negocio')
    descripcion = models.CharField(max_length=1000, verbose_name='Descripción')

    def __str__(self):
        return f"Producto: {self.nombre} - Precio: {self.precio}"

    def eliminar(self, using=None, keep_parents=False):
        self.imagen.storage.delete(self.imagen)
        super().delete()

# Tabla de reserva
class Reserva(models.Model):
    id_reserva = models.AutoField(primary_key=True)
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservas_cliente', verbose_name='Cliente')
    negocio = models.ForeignKey(Negocio, on_delete=models.CASCADE, verbose_name='Negocio') 
    administrador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservas_administrador', verbose_name='Administrador')
    fecha = models.DateField(verbose_name='Fecha de la reserva')
    hora = models.TimeField(verbose_name='Hora de la reserva')
    numero_personas = models.IntegerField(verbose_name='Número de personas')
    correo_cliente = models.EmailField(verbose_name='Correo del cliente')
    telefono_cliente = models.CharField(max_length=15, verbose_name='Teléfono del cliente')

    def __str__(self):
        return f"Reserva de {self.cliente.username} para {self.numero_personas} personas el {self.fecha} a las {self.hora}"


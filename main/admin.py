from django.contrib import admin
from .models import *

# Registramos los modelos para que el admin ya los tenga .

admin.site.register(Negocio)
admin.site.register(Producto)
admin.site.register(Reserva)
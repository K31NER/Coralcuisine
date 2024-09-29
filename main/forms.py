from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *

class RegistroForm(UserCreationForm):
    user_type = forms.ChoiceField(choices=[('Administrador', 'Administrador'), ('Cliente', 'Cliente')], label='Tipo de cuenta')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'user_type']  # user_type no es parte del modelo, solo se usa en el formulario

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return password2
    
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'precio', 'descripcion', 'imagen']
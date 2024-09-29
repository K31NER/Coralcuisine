from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from .forms import *
from django.contrib.auth import login
from .models import *
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

#manejo de grupos
#verificadores de grupo
def es_cliente(user):
    return user.groups.filter(name='Cliente').exists()
def es_admin(user):
    return user.groups.filter(name='Administrador').exists()

#paginas disponibles para cada grupo
class ClienteView(LoginRequiredMixin, TemplateView):
    inicio = 'inicio.html' 
    reservas = 'reservas.html' 
    form = 'form_reserva.html'  
    editar_reserva = 'editar_reserva.html'

class AdminView(LoginRequiredMixin, TemplateView):
    inicio_admin = 'admin/inicio_admin.html'
    inventario = 'admin/inventario.html'
    crear = 'admin/creacion_productos.html'
    editar_producto = 'admin/editar_producto.html'
    reservas_admin = 'admin/reservas_admin.html'
    
# vistas de las paginas
def login_views(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirigir según el grupo del usuario
            if user.groups.filter(name='Administrador').exists():
                return redirect('vista')  # Redirigir a la página del administrador
            elif user.groups.filter(name='Cliente').exists():
                return redirect('inicio')  # Redirigir a la página del cliente
        else:
            # Si la autenticación falla
            return render(request, 'login.html', {'error': 'Nombre de usuario o contraseña incorrectos'})
    return render(request, 'login.html')


def registro(request):
    error_message = None 
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()  

            # Asignar el grupo según el tipo de usuario
            if form.cleaned_data['user_type'] == 'Administrador':
                group = Group.objects.get(name='Administrador')
                user.groups.add(group)  # Agregar el usuario al grupo correspondiente
                
                # Autenticar y hacer login del usuario
                user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
                if user is not None:
                    login(request, user)  # Loguear al usuario
                    return redirect('negocio')  # Redirigir a la vista de creación de negocio si es Administrador

            else:
                group = Group.objects.get(name='Cliente')
                user.groups.add(group)  # Agregar el usuario al grupo correspondiente

            return redirect('login')  # Redirigir al login tras el registro exitoso
        else:
            error_message = "Por favor, corrija los errores en el formulario."  # Mensaje de error

    else:
        form = RegistroForm()
    
    return render(request, 'registro.html', {'form': form, 'error_message': error_message}) 


def inicio(request):
    #obtenemos la informacion del modelo
    productos = Producto.objects.all()
    #verificamos si la informacion llega
    #print(productos)
    return render(request,'inicio.html',{'productos':productos})#vinculamos con la vista

@login_required(login_url='login')
@user_passes_test(es_cliente)
def reservas(request):
    reservas_cliente = Reserva.objects.filter(cliente=request.user)
    return render(request,'reservas.html',{'reservas': reservas_cliente})

@login_required(login_url='login')
@user_passes_test(es_admin)
def inicio_admin(request):
    productos = Producto.objects.all()
    return render(request,'admin/inicio_admin.html',{'productos':productos})#vinculamos con la vista

    

@user_passes_test(es_admin)
@login_required(login_url='login')
def inventario(request):
    # Obtener el negocio asociado al usuario autenticado
    negocio = get_object_or_404(Negocio, usuario_administrador=request.user)

    # Filtrar los productos por el negocio del usuario
    productos = Producto.objects.filter(id_negocio=negocio)
    
    return render(request,'admin/inventario.html',{'productos':productos})

@login_required(login_url='login')
@user_passes_test(es_admin)
def reservas_admin(request):
    reservas = Reserva.objects.filter(administrador=request.user)

    return render(request,'admin/reservas_admin.html',{'reservas':reservas})


@login_required(login_url='login')
@user_passes_test(es_cliente)
def form_reserva(request,producto_id):
    producto = get_object_or_404(Producto, id_producto=producto_id)
    if request.method == 'POST':
        numero_contacto = request.POST['numero de contacto']
        personas = request.POST['personas']
        fecha = request.POST['fecha']
        hora = request.POST.get('hora')

        # Obtener el administrador a partir del producto
        administrador = producto.id_negocio.usuario_administrador

        # Crear la reserva
        reserva = Reserva(
            cliente=request.user,
            administrador=administrador,
            negocio=producto.id_negocio,
            numero_personas=personas,
            fecha=fecha,
            hora=hora,
            correo_cliente=request.user.email,
            telefono_cliente=numero_contacto
        )
        reserva.save()

        # Enviar correo al cliente
        subject_cliente = 'Confirmación de tu reserva'
        context_cliente = {
            'nombre': request.user.username,
            'personas': personas,
            'fecha': fecha,
            'hora': hora,
            'negocio': producto.id_negocio.nombre_negocio,
            'numero_local': producto.id_negocio.numero_de_local,
        }
        html_message_cliente = render_to_string('correo/correo_c.html', context_cliente)
        email_cliente = EmailMultiAlternatives(subject_cliente, "", settings.DEFAULT_FROM_EMAIL, [request.user.email])
        email_cliente.attach_alternative(html_message_cliente, "text/html")
        email_cliente.send()

        # Enviar correo al administrador
        subject_admin = 'Nueva reserva'
        context_admin = {
            'nombre': administrador.username,
            'cliente': request.user.username,
            'personas': personas,
            'fecha': fecha,
            'hora': hora,
            'negocio': producto.id_negocio.nombre_negocio,
            'numero_local': producto.id_negocio.numero_de_local,
        }
        html_message_admin = render_to_string('correo/correo_a.html', context_admin)
        email_admin = EmailMultiAlternatives(subject_admin, "", settings.DEFAULT_FROM_EMAIL, [administrador.email])
        email_admin.attach_alternative(html_message_admin, "text/html")
        email_admin.send()

        messages.success(request, 'Reserva creada con éxito. Se ha enviado un correo de confirmación.')
        return redirect('inicio')

    return render(request, 'form_reserva.html', {'producto': producto})

@login_required(login_url='login')
@user_passes_test(es_admin)
def creacion_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save(commit=False)
            # Obtener el negocio relacionado al usuario autenticado
            negocio = get_object_or_404(Negocio, usuario_administrador=request.user)
            producto.id_negocio = negocio
            producto.save()
            return redirect('inventario')  # Redirigir al inventario o donde desees
    else:
        form = ProductoForm()
    
    return render(request,'admin/creacion_productos.html',  {'form': form})

@login_required(login_url='login')
@user_passes_test(es_admin)
def editar_producto(request, id_producto=None):
    producto = get_object_or_404(Producto, id_producto=id_producto)

    if request.method == 'POST':
        # Actualizar el producto con los datos enviados
        producto.nombre = request.POST.get('nombre')
        producto.precio = request.POST.get('precio')
        producto.descripcion = request.POST.get('descripcion')
        
        # Si se sube una nueva imagen, reemplazarla
        if request.FILES.get('imagen'):
            producto.imagen = request.FILES.get('imagen')

        producto.save()
        return redirect('inventario')  # Redirigir al inventario tras guardar los cambios
    
    return render(request, 'admin/editar_producto.html', {'producto': producto})



@user_passes_test(es_admin)
@login_required(login_url='login')
def negocio(request):
    if request.method == "POST":
        logo_negocio = request.FILES.get('logo_negocio')
        nombre_negocio = request.POST.get('nombre_negocio')
        telefono = request.POST.get('telefono')
        numero_de_local = request.POST.get('numero_de_local')
        correo_de_local = request.POST.get('correo_de_local')
        
        # Crear el negocio
        negocio = Negocio(
            logo_negocio=logo_negocio,
            nombre_negocio=nombre_negocio,
            telefono=telefono,
            numero_de_local=numero_de_local,
            correo_de_local=correo_de_local,
            usuario_administrador=request.user  # Asignar el usuario actual como administrador
        )
        negocio.save()  # Guardar el negocio

        return redirect('vista')  # Redirigir a una vista específica después del registro

    return render(request, 'admin/negocio.html')

@user_passes_test(es_admin)
@login_required(login_url='login')
def eliminar_producto(request, id_producto):
    producto = get_object_or_404(Producto, id_producto=id_producto)
    producto.delete()
    messages.success(request, 'Producto eliminado con éxito.')
    return redirect('inventario')  


@login_required(login_url='login')
@user_passes_test(es_cliente)
def eliminar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id_reserva=reserva_id)

    # Obtener datos necesarios para el correo
    cliente_email = reserva.correo_cliente
    nombre_cliente = reserva.cliente.username
    numero_personas = reserva.numero_personas
    fecha = reserva.fecha
    hora = reserva.hora
    administrador_email = reserva.administrador.email  # Correo del administrador

    # Eliminar la reserva
    reserva.delete()

    # Enviar correo de cancelación al cliente
    subject_cliente = 'Cancelación de reserva'
    context_cliente = {
        'nombre': nombre_cliente,
        'numero_personas': numero_personas,
        'fecha': fecha,
        'hora': hora,
    }
    message_cliente = render_to_string('correo/eliminar_c.html', context_cliente)
    
    email_cliente = EmailMultiAlternatives(subject_cliente, '', settings.DEFAULT_FROM_EMAIL, [cliente_email])
    email_cliente.attach_alternative(message_cliente, 'text/html')  # Cambiado aquí
    email_cliente.send()

    # Enviar correo de cancelación al administrador
    subject_administrador = 'Reserva Cancelada'
    context_administrador = {
        'nombre_cliente': nombre_cliente,
        'numero_personas': numero_personas,
        'fecha': fecha,
        'hora': hora,
    }
    message_administrador = render_to_string('correo/eliminar_a.html', context_administrador)

    email_administrador = EmailMultiAlternatives(subject_administrador, '', settings.DEFAULT_FROM_EMAIL, [administrador_email])
    email_administrador.attach_alternative(message_administrador, 'text/html')  # Cambiado aquí
    email_administrador.send()

    messages.success(request, 'Reserva cancelada con éxito. Se han enviado correos de confirmación de cancelación.')
    return redirect('reservas')  # Redirige a la vista de reservas

@login_required(login_url='login')
@user_passes_test(es_admin)
def eliminar_reserva_admin(request, reserva_id):
    reserva = get_object_or_404(Reserva, id_reserva=reserva_id)

    # Obtener datos necesarios para el correo
    cliente_email = reserva.correo_cliente
    nombre_cliente = reserva.cliente.username
    numero_personas = reserva.numero_personas
    fecha = reserva.fecha
    hora = reserva.hora

    # Eliminar la reserva
    reserva.delete()

    # Enviar correo de cancelación al cliente
    subject_cliente = 'Cancelación de reserva'
    context_cliente = {
        'nombre': nombre_cliente,
        'numero_personas': numero_personas,
        'fecha': fecha,
        'hora': hora,
    }
    message_cliente = render_to_string('correo/eliminar_c.html', context_cliente)
    
    email_cliente = EmailMultiAlternatives(subject_cliente, '', settings.DEFAULT_FROM_EMAIL, [cliente_email])
    email_cliente.attach_alternative(message_cliente, 'text/html')
    email_cliente.send()

    # Enviar correo al administrador sobre la cancelación
    subject_administrador = 'Reserva Cancelada por el Administrador'
    context_administrador = {
        'nombre_cliente': nombre_cliente,
        'numero_personas': numero_personas,
        'fecha': fecha,
        'hora': hora,
    }
    message_administrador = render_to_string('correo/eliminar_a.html', context_administrador)

    # Aquí puedes enviar un correo al administrador si es necesario
    email_administrador = EmailMultiAlternatives(subject_administrador, '', settings.DEFAULT_FROM_EMAIL, [request.user.email])  # Puedes cambiar el destinatario si es necesario
    email_administrador.attach_alternative(message_administrador, 'text/html')
    email_administrador.send()

    messages.success(request, 'Reserva cancelada con éxito. Se han enviado correos de confirmación de cancelación.')
    return redirect('calendario')  # Redirige a la vista de reservas

@login_required(login_url='login')
@user_passes_test(es_cliente)
def editar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id_reserva=reserva_id)
    if request.method == 'POST':
        # Obtener los nuevos datos del formulario
        numero_contacto = request.POST['telefono']
        personas = request.POST['personas']
        fecha = request.POST['fecha']
        hora = request.POST.get('hora')

        # Actualizar la reserva
        reserva.numero_personas = personas
        reserva.fecha = fecha
        reserva.hora = hora
        reserva.telefono_cliente = numero_contacto
        reserva.save()

        # Enviar correo al cliente
        subject_cliente = 'Actualización de tu reserva'
        context_cliente = {
            'nombre': request.user.username,
            'personas': personas,
            'fecha': fecha,
            'hora': hora,
            'negocio': reserva.negocio.nombre_negocio,
            'numero_local': reserva.negocio.numero_de_local,
        }
        html_message_cliente = render_to_string('correo/actualizacion_c.html', context_cliente)
        email_cliente = EmailMultiAlternatives(subject_cliente, "", settings.DEFAULT_FROM_EMAIL, [request.user.email])
        email_cliente.attach_alternative(html_message_cliente, "text/html")
        email_cliente.send()

        # Enviar correo al administrador
        subject_admin = 'Reserva Actualizada'
        context_admin = {
            'nombre': reserva.administrador.username,
            'cliente': request.user.username,
            'personas': personas,
            'fecha': fecha,
            'hora': hora,
            'negocio': reserva.negocio.nombre_negocio,
            'numero_local': reserva.negocio.numero_de_local,
        }
        html_message_admin = render_to_string('correo/actualizacion_a.html', context_admin)
        email_admin = EmailMultiAlternatives(subject_admin, "", settings.DEFAULT_FROM_EMAIL, [reserva.administrador.email])
        email_admin.attach_alternative(html_message_admin, "text/html")
        email_admin.send()

        messages.success(request, 'Reserva actualizada con éxito. Se ha enviado un correo de confirmación.')
        return redirect('reservas')

    # Para el método GET, muestra el formulario con los datos existentes
    return render(request, 'editar_reserva.html', {'reserva': reserva})


def negocio_logo(request):
    negocios = Negocio.objects.all()
    return render(request, 'negocios_logo.html', {'negocios':negocios})

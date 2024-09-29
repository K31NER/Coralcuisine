from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

#creamos las redirecciones de la pagina 
urlpatterns = [
    path('',views.inicio,name="inicio"),
    path('login/',views.login_views,name="login"),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('registro/',views.registro,name="registro"),
    path('inventario/',views.inventario,name='inventario'),
    path('reservas/',views.reservas,name='reservas'),
    path('calendario/',views.reservas_admin,name='calendario'),
    path('vista/',views.inicio_admin,name="vista"),
    path('form/<int:producto_id>/',views.form_reserva,name='form_reserva'),
    path('inventario/creacion/',views.creacion_producto,name='creacion'),
    path('inventario/editor/<int:id_producto>/',views.editar_producto,name='editor'),
    path('reservas/<int:reserva_id>/', views.editar_reserva, name='edit_reserva'),
    path('registro/negocio',views.negocio,name='negocio'),
    path('negocios/',views.negocio_logo,name="negocios"),
    
    #urls para eliminar productos
    path('inventario/borrar/<int:id_producto>/', views.eliminar_producto, name='eliminar_producto'),
    path('eliminar_reserva/<int:reserva_id>/', views.eliminar_reserva, name='eliminar_reserva'),
    path('eliminar_reserva_admin/<int:reserva_id>/', views.eliminar_reserva_admin,name='eliminar_reserva_admin'),

]

#configuramos la carga de imagenes de manera correcta
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
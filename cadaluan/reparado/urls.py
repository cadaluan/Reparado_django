from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.documentation import include_docs_urls
from rest_framework.authtoken.views import obtain_auth_token
from .views import RegisterView

from . import views

router = DefaultRouter()
router.register(r'usuario', views.UsuarioViewSet)
router.register(r'categoria', views.CategoriaViewSet)
router.register(r'servicio', views.ServicioViewSet)
router.register(r'solicitud', views.SolicitudViewSet)
router.register(r'comentario', views.ComentarioViewSet)
"""router.register(r'auditoria', views.AuditoriaViewSet)"""
router.register(r'factura', views.FacturaViewSet)
"""router.register(r'metodo_pago', views.MetodoPagoViewSet)"""
"""router.register(r'factura_pago', views.FacturaPagoViewSet)"""

urlpatterns = [
    # URL API's del Proyecto
    path("api/1.0/", include(router.urls)),
    path('api/1.0/docs/', include_docs_urls(title='Reparado API')),
    path('api/1.0/servicios_por_cat/<int:categorias>/', views.ServicioFiltroCategoria.as_view()),

    # Ruta para login y obtener token desde app móvil
    path('api/1.0/token-auth/', views.CustomAuthToken.as_view()),

    # Ruta para login en API web
    path('api/1.0/auth/', include("rest_framework.urls")),

    # Ruta para registrar usuario por api a app movil
   
    path('api/1.0/register/', views.RegisterView.as_view(), name='register'),


    # Inicio de sesión
    path('', views.index, name='index'),
    path("calendario/", views.calendario, name="calendario"),
    path("login/", views.login, name="login"),
    path("inicio/", views.inicio, name="inicio"),
    path("logout/", views.logout, name="logout"),
    path("registro/", views.registro, name="registro"),
    path("cambiar_clave/", views.cambiar_clave, name="cambiar_clave"),
    path("recuperar_clave/", views.recuperar_clave, name="recuperar_clave"),
    path("verificar_token_form/<str:email>/", views.verificar_token_form, name="verificar_token_form"),
    path("olvide_mi_clave/<str:email>/", views.olvide_mi_clave, name="olvide_mi_clave"),

    # Categorías
    path("categorias/", views.categorias, name="categorias"),
    path("categorias_crear/", views.categorias_crear, name="categorias_crear"),
    path("categorias_editar/<int:id_categoria>/", views.categorias_editar, name="categorias_editar"),
    path("categorias_eliminar/<int:id_categoria>/", views.categorias_eliminar, name="categorias_eliminar"),

    # Servicios
    path("servicios/", views.servicios, name="servicios"),
    path("servicios_crear/", views.servicios_crear, name="servicios_crear"),
    path("servicios_editar/<int:id_servicio>/", views.servicios_editar, name="servicios_editar"),
    path("servicios_eliminar/<int:id_servicio>/", views.servicios_eliminar, name="servicios_eliminar"),

    # Solicitudes
    path("solicitudes/", views.solicitudes, name="solicitudes"),
    path("solicitud_servicio/<int:id_servicio>/", views.solicitud_servicio, name="solicitud_servicio"),
    path("solicitud_editar/<int:id_solicitud>/", views.solicitud_editar, name="solicitud_editar"),
    path("solicitud_eliminar/<int:id_solicitud>/", views.solicitud_eliminar, name="solicitud_eliminar"),

    # Usuarios
    path("usuarios/", views.usuarios, name="usuarios"),
    path("usuarios_crear/", views.usuarios_crear, name="usuarios_crear"),
    path("usuarios_visualizar/<int:id_usuario>/", views.usuarios_visualizar, name="usuarios_visualizar"),
    path("visualizar_perfil/<int:id_usuario>/", views.visualizar_perfil, name="visualizar_perfil"),
    path("usuarios_editar/<int:id_usuario>/", views.usuarios_editar, name="usuarios_editar"),
    path("usuarios_eliminar/<int:id_usuario>/", views.usuarios_eliminar, name="usuarios_eliminar"),

    # Carro de compras
    path("carrito_add/", views.carrito_add, name="carrito_add"),
    path("ver_carrito/", views.ver_carrito, name="ver_carrito"),
    path("eliminar_item_carrito/<int:id_solicitud>/", views.eliminar_item_carrito, name="eliminar_item_carrito"),
    path("vaciar_carrito/", views.vaciar_carrito, name="vaciar_carrito"),
    path("guardar_compra/", views.guardar_compra, name="guardar_compra"),
    path("detalle_compra/<int:compra_id>/", views.detalle_compra, name="detalle_compra"),
    path("detalle_compras/", views.detalle_compras, name="detalle_compras"),

    # Correo
    path("enviar_correo/", views.enviar_correo, name="enviar_correo"),
]

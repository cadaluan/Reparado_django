from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from .authentication import CustomUserManager


# Create your models here.
class Categoria(models.Model):
    nombre_cat = models.CharField(max_length=100)
    desc = models.TextField()
    objects = models.Manager()

    def __str__(self):
        return f"{self.nombre_cat}"

    class Meta:
        verbose_name_plural = "Categoría"


class Usuario(AbstractUser):
    nombre = models.CharField(max_length=254, blank=True, null=True)
    apellido = models.CharField(max_length=254, blank=True, null=True)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=254)
    email = models.EmailField(max_length=254, unique=True, blank=True, null=True)
    direccion = models.CharField(max_length=254, blank=True, null=True)
    telefono = models.CharField(max_length=15, unique=True, blank=True, null=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    foto = models.ImageField(upload_to="usuarios/", default="usuarios/default.png", blank=True, null=True)
    token = models.CharField(max_length=10, null=True, blank=True)
    activo = models.BooleanField(default=True)
    objects = CustomUserManager()

    ROLES = (
        ("ADMIN", "Administrador"),
        ("SEC", "Secretaria"),
        ("TEC", "Técnico"),
        ("USU", "Usuario"),
    )
    rol = models.CharField(max_length=5, choices=ROLES, default="USU", null=True, blank=True)
    categorias = models.ManyToManyField(Categoria, blank=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    class Meta:
        verbose_name_plural = "Usuario"


class Servicio(models.Model):
    categoria = models.ForeignKey('Categoria', on_delete=models.DO_NOTHING)
    nombre_ser = models.CharField(max_length=200)
    desc_ser = models.TextField()
    precio = models.IntegerField()
    tiempo_estimado = models.IntegerField(default=120)  # Tiempo en minutos
    foto = models.ImageField(upload_to="productos/", default="productos/default.png")
    objects = models.Manager()

    def __str__(self):
        return self.nombre_ser

    class Meta:
        verbose_name_plural = "Servicio"


class Solicitud(models.Model):
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField()
    precio = models.IntegerField()
    tiempo_estimado = models.IntegerField(default=120)  # Tiempo en minutos
    zona = models.CharField(max_length=200)
    usuario = models.ForeignKey('Usuario', on_delete=models.DO_NOTHING, related_name='solicitudes_usuario')
    tecnico = models.ForeignKey('Usuario', on_delete=models.DO_NOTHING, related_name='solicitudes_tecnico', blank=True,
                                null=True)

    ESTADOS = [
        ("EN_ESPERA", 'En espera'),
        ("EN_PROGRESO", 'En progreso'),
        ("COMPLETADO", 'Completado'),
        ("CANCELADO_PROVEEDOR", 'Cancelado por el proveedor'),
        ("CANCELADO_USUARIO", 'Cancelado por el usuario'),
        ("PROGRAMADO", 'Programado'),
    ]
    estado = models.CharField(max_length=50, choices=ESTADOS, default="EN_ESPERA")
    objects = models.Manager()

    def __str__(self):
        return str(self.id)

    def categoria(self):
        return self.servicio.categoria

    def fecha_final(self):
        return self.fecha_hora + timedelta(minutes=self.tiempo_estimado)

    class Meta:
        verbose_name_plural = "Solicitud"


class Comentario(models.Model):
    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE)
    estado = models.CharField(max_length=200)
    comentario = models.CharField(max_length=254)
    estrellas = models.IntegerField()
    objects = models.Manager()

    def __str__(self):
        return f"Comentario para Solicitud {self.solicitud}"

    class Meta:
        verbose_name_plural = "Comentario"


class Compra(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING)
    fecha = models.DateTimeField(auto_now_add=True)
    ESTADO = [
        (1, "Creado"),
        (2, "Enviado"),
        (3, "Cancelado"),
    ]
    estado = models.IntegerField(choices=ESTADO, default=1, blank=True)
    objects = models.Manager()

    def __str__(self):
        return f"{self.id} - {self.usuario}"

    class Meta:
        verbose_name_plural = "Compras"


class Factura(models.Model):
    METODOS_PAGO = [
        ("EFECTIVO", "Efectivo"),
        ("TARJETA_DEBITO", "Tarjeta de débito"),
        ("TARJETA_CREDITO", "Tarjeta de crédito"),
        ("TRANSFERENCIA_BANCARIA", "Transferencia bancaria"),
        ("PAYPAL", "PayPal"),
        ("CHEQUE", "Cheque"),
    ]

    FORMAS_PAGO = [
        ("CONTADO", "Pago al contado"),
        ("CREDITO", "Pago mediante crédito"),
        ("DEBITO_AUTOMATICO", "Pago mediante débito automático"),
        ("TRANSFERENCIA_BANCARIA", "Pago mediante transferencia bancaria"),
        ("TARJETA_CREDITO", "Pago con tarjeta de crédito"),
        ("TARJETA_DEBITO", "Pago con tarjeta de débito"),
    ]

    compra = models.ForeignKey(Compra, on_delete=models.CASCADE)
    fecha_emision = models.DateField(default=timezone.now)
    total = models.IntegerField()
    metodo_pago = models.CharField(max_length=50, choices=METODOS_PAGO, default="EFECTIVO")
    forma_pago = models.CharField(max_length=50, choices=FORMAS_PAGO, default="CONTADO")
    fecha_pago = models.DateField(default=timezone.now)
    objects = models.Manager()

    class Meta:
        verbose_name_plural = "Facturas"

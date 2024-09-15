import json
from datetime import datetime
from random import randint
from .models import *
from django.conf import settings
from django.contrib import messages
from django.core.mail import BadHeaderError, EmailMessage
from django.db import transaction
from django.db.models import F, ExpressionWrapper, DateTimeField, DurationField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_http_methods
from rest_framework import viewsets, generics, status

from .encriptar import *
from .forms import *
from .serializers import *

from rest_framework.authtoken.views import ObtainAuthToken, APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


def calendario(request):
    logueo = request.session.get("logueo", False)
    if logueo:
        sol = Solicitud.objects.all()
        solicitudes_realizadas = []

        for item in sol:
            tiempo_estimado = item.servicio.tiempo_estimado
            end_time = item.fecha_hora + timedelta(minutes=tiempo_estimado)
            solicitudes_realizadas.append({
                "title": item.usuario.nombre,
                "start": item.fecha_hora.strftime("%Y-%m-%d %H:%M:%S"),
                "end": end_time.strftime("%Y-%m-%d %H:%M:%S"),
            })

        context = {"solicitudes": json.dumps(solicitudes_realizadas)}
        return render(request, "reparado/calendario/calendario.html", context)
    else:
        messages.warning(request, "No ha iniciado sesión...")
        return render(request, "reparado/layouts/nuevo_login.html")


def index(request):
    logueo = request.session.get("logueo", False)
    if logueo:
        return redirect("inicio")  # direcciona a la vista llamada inicio
    else:
        return render(request, "reparado/layouts/nuevo_login.html")


def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        try:
            q = Usuario.objects.get(username=username)
            verify = verify_password(password, q.password)
            if verify:
                messages.success(request, f"Bienvenido {q.username}")
                # Crear la sesión...
                request.session["logueo"] = {
                    "id": q.id,
                    "nombre": q.nombre,
                    "rol": q.rol,
                    "username": q.username,
                }
                request.session["carrito"] = []
                request.session["items_carrito"] = 0
                request.session["total_carrito"] = 0
                return redirect("inicio")
            else:
                raise Exception(verify)
        except Exception as e:
            messages.error(request, f"Usuario o contraseña no válidos... {e}")
            return redirect("index")
    else:
        messages.warning(request, "No se enviaron datos...")
        return redirect("index")


def inicio(request):
    logueo = request.session.get("logueo", False)
    if logueo:
        return render(request, "reparado/home/index.html")
    else:
        return redirect("index")


def logout(request):
    logueo = request.session.get("logueo", False)
    if logueo:
        del request.session["logueo"]
        del request.session["carrito"]
        del request.session["items_carrito"]
        del request.session["total_carrito"]
        return redirect("index")
    else:
        messages.info(request, "No se pudo cerrar sesión, intente de nuevo")
        return redirect("inicio")


def cambiar_clave(request):
    logueo = request.session.get("logueo", False)
    if logueo:
        if request.method == "GET":
            return render(request, "reparado/usuarios/cambiar_contraseña.html")
        elif request.method == "POST":
            # capturo la clave actual del formulario
            old_password = request.POST.get("old_password")
            new_password1 = request.POST.get("new_password1")
            new_password2 = request.POST.get("new_password2")
            # capturo variable de sesión para averiguar ID de usuario
            logueo = request.session.get("logueo", False)
            q = Usuario.objects.get(pk=logueo["id"])
            verify = verify_password(old_password, q.password)
            if verify:
                if new_password1 == new_password2:
                    # modifico clave al usuario actual (al objeto)
                    clave = hash_password(new_password1)
                    q.password = clave
                    # guardo en base de datos
                    q.save()
                    messages.success(request, "Clave cambiada correctamente!!")
                    return render(request, "reparado/home/index.html")
                else:
                    messages.warning(request, "Claves nuevas no concuerdan...")
            else:
                messages.error(request, "Clave actual no corresponde...")
        return redirect("index")
    else:
        messages.error(request, "No hay sesión activa...")
        return render(request, "reparado/layouts/nuevo_login.html")


def recuperar_clave(request):
    if request.method == 'GET':
        return render(request, "reparado/usuarios/recuperar_clave.html")
    elif request.method == "POST":
        try:
            q = Usuario.objects.get(email=request.POST.get("email"))
            print(q)
            num = randint(100000, 999999)
            # convertir num a base64 para ocultarlo un poco
            ofuscado = base64.b64encode(str(num).encode("ascii")).decode("ascii")
            q.token = ofuscado
            q.save()
            # envío de correo
            ruta = reverse(verificar_token_form, args=(q.email,))
            resultado = enviar_correo(ruta, q.email, q.token)
            print(q)
            messages.info(request, resultado)
            return redirect("verificar_token_form", email=q.email)
        except Usuario.DoesNotExist:
            messages.error(request, "Usuario no existe...")
        return redirect("recuperar_clave")
    else:
        messages.error(request, "Usuario no existe...")


def verificar_token_form(request, email):
    if request.method == "POST":
        try:
            q = Usuario.objects.get(email=email)
            if q.token != "" and q.token == request.POST.get("token"):
                messages.success(request, "Token OK, cambie su clave!!")
                return redirect("olvide_mi_clave", email=email)
            else:
                messages.error(request, "Token no válido...")
        except Usuario.DoesNotExist:
            messages.error(request, "Usuario no existe...")
        return redirect("verificar_token_form", email=email)
    else:
        contexto = {"email": email}
        return render(request, "reparado/usuarios/verificar_token_form.html", contexto)


def olvide_mi_clave(request, email):
    if request.method == "POST":
        c_nueva1 = request.POST.get("nueva1")
        c_nueva2 = request.POST.get("nueva2")
        q = Usuario.objects.get(email=email)
        if c_nueva1 == c_nueva2:
            # modifico clave al usuario actual (al objeto)
            clave = hash_password(c_nueva1)
            q.password = clave
            # eliminar el token de db
            q.token = ""
            # guardo en base de datos
            q.save()
            messages.success(request, "Clave cambiada correctamente!!")
            return redirect("index")
        else:
            messages.warning(request, "Claves nuevas no concuerdan...")
        return redirect("olvide_mi_clave", email=email)
    else:
        contexto = {"email": email}
        return render(request, "reparado/usuarios/olvide_mi_clave.html", contexto)


def handle_uploaded_file(f):
    with open(f"{settings.MEDIA_ROOT}/usuarios/{f.name}", "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def registro(request):
    if request.method == 'GET':
        return render(request, 'reparado/usuarios/registro.html')

    elif request.method == 'POST':
        username = request.POST.get("username").strip()
        password1 = request.POST.get("password1").strip()
        password2 = request.POST.get("password2").strip()

        # Validaciones
        if not username or not password1 or not password2:
            messages.error(request, "Los campos no pueden estar vacíos")
            return redirect("index")

        if Usuario.objects.filter(username=username).exists():
            messages.error(request, "Username ya existe")
            return redirect("index")

        pattern = r'^(?!.*\.\.)(?!.*[&=_\'\-+,<>])([a-zA-Z0-9]+(\.[a-zA-Z0-9]+)*)$'
        if not re.match(pattern, username):
            messages.error(request, 'El nombre de usuario no es válido. Solo se permiten letras, números y puntos (.). '
                                    'No se permiten dos puntos consecutivos ni los siguientes caracteres: & = _ \' - '
                                    '+ , < >')

        if password1 != password2:
            messages.warning(request, "Las contraseñas no coinciden")
            return redirect("index")

        clave = hash_password(password1)

        q = Usuario(
            username=username,
            password=clave,
        )

        q.save()

        messages.success(request, "Registro exitoso!")

        request.session["logueo"] = {
            "id": q.id,
            "username": q.username,
            "nombre": q.nombre,
            "rol": q.rol,
        }
        request.session["carrito"] = []
        request.session["items_carrito"] = 0
        request.session["total_carrito"] = 0
        return redirect("inicio")
    else:
        return render(request, 'reparado/usuarios/registro.html')


def categorias(request):
    logueo = request.session.get("logueo", False)
    if logueo:
        q = Categoria.objects.all()
        context = {"data": q}
        return render(request, "reparado/categorias/categorias_listar.html", context)
    else:
        messages.info(request, "Inicie sesión")
        return redirect("index")


def categorias_crear(request):
    logueo = request.session.get("logueo", False)

    if not logueo:
        messages.info(request, "Debe iniciar sesión como administrador.")
        return redirect("index")

    if logueo.get("rol") != "ADMIN":
        messages.info(request, "No tiene permisos para acceder al módulo.")

    if request.method == "GET":
        return render(request, "reparado/categorias/categorias_crear.html")

    if request.method == "POST":
        nombre_cat = request.POST.get("nombre_cat").strip()
        desc = request.POST.get("desc").strip()

        if not nombre_cat or not desc:
            messages.error(request, "Los campos no pueden estar vacíos")
            return redirect("categorias_crear")

        regex = r'^(?!.* {2})(?!.*\.\.)(?!.*\s$)[A-Za-zÁÉÍÓÚáéíóúÑñ ,.¡!¿?]*$'

        if not re.match(regex, nombre_cat):
            messages.error(request, "El nombre no puede contener números ni caracteres especiales")
            return redirect("categorias_crear")

        if not re.match(regex, desc):
            messages.error(request, "La descripción no puede contener números ni caracteres especiales")
            return redirect("categorias_crear")

        try:
            q = Categoria(nombre_cat=nombre_cat, desc=desc)
            q.save()
            messages.success(request, "Categoría guardada exitosamente.")
        except Exception as e:
            messages.error(request, f"Error: {e}")
        return redirect("categorias")


@require_http_methods(["GET", "POST"])
def categorias_editar(request, id_categoria):
    try:
        categoria = Categoria.objects.get(pk=id_categoria)
        logueo = request.session.get("logueo", False)

        if not logueo:
            messages.info(request, "Debe iniciar sesión como administrador...")
            return redirect("index")

        if logueo.get("rol") != "ADMIN":
            messages.info(request, "No tiene permisos para acceder al módulo...")
            return redirect("index")

        if request.method == 'GET':
            return render(request, 'reparado/categorias/categoria_editar_modal.html', {'categoria': categoria})

        if request.method == 'POST':
            nombre_cat = request.POST.get('nombre_cat', '').strip()
            desc = request.POST.get('desc', '').strip()

            # Validaciones
            regex = r'^(?!.* {2})(?!.*\.\.)(?!.*\s$)[A-Za-zÁÉÍÓÚáéíóúÑñ ,.¡!¿?]*$'

            if not nombre_cat or not desc:
                messages.error(request, "Todos los campos son obligatorios y no pueden estar vacíos.")
                return redirect("categorias")
            elif not re.match(regex, nombre_cat):
                messages.error(request,
                               "El nombre de la categoría no es válido. No debe contener números ni caracteres "
                               "especiales.")
                return redirect("categorias")
            elif not re.match(regex, desc):
                messages.error(request,
                               "La descripción no es válida. No debe contener números ni caracteres especiales.")
                return redirect("categorias")
            else:
                # Si las validaciones son correctas, se actualiza la categoría
                categoria.nombre_cat = nombre_cat
                categoria.desc = desc
                categoria.save()
                messages.success(request, 'Datos actualizados con éxito!!!')
                return redirect("categorias")

        return render(request, 'reparado/categorias/categoria_editar_modal.html', {'categoria': categoria})

    except Categoria.DoesNotExist:
        messages.error(request, "La categoría no existe.")
        return redirect("index")
    except Exception as e:
        messages.error(request, f"Se produjo un error: {e}")
        return redirect("index")


def categorias_eliminar(request, id_categoria):
    try:
        categoria = Categoria.objects.get(pk=id_categoria)
        logueo = request.session.get("logueo", False)

        if not logueo:
            messages.info(request, "Debe iniciar sesión como administrador")
            return redirect("index")

        if logueo.get("rol") != "ADMIN":
            messages.info(request, "No tiene permisos para acceder al módulo...")
            return redirect("index")

        if request.method == "GET":
            return render(request, 'reparado/categorias/categoria_eliminar_modal.html', {'categoria': categoria})

        if request.method == 'POST':
            # Procesa el formulario y actualiza la base de datos
            categoria.delete()
            messages.success(request, 'Categoría eliminada con éxito...')

    except Categoria.DoesNotExist:
        messages.error(request, "La categoría no existe.")
        return redirect("categorias")

    except Exception as e:
        messages.error(request, f"Se produjo un error: {e}")
        return redirect("index")

    return redirect("categorias")


def servicios(request):
    logueo = request.session.get("logueo", False)
    q = Servicio.objects.all()
    context = {"data": q}
    if logueo:
        return render(request, "reparado/servicios/servicios_listar.html", context)
    else:
        messages.error(request, "Debe iniciar sesión.")
        return redirect("index")


def servicios_crear(request):
    logueo = request.session.get("logueo", False)
    categoria = Categoria.objects.all()
    context = {"categoria": categoria}

    if not logueo:
        messages.info(request, "Debe iniciar sesión como administrador...")
        return redirect("index")

    if logueo.get("rol") != "ADMIN":
        messages.info(request, "No tiene permisos para acceder al módulo.")
        return redirect("index")

    if request.method == "GET":
        return render(request, "reparado/servicios/servicios_crear.html", context)

    if request.method == "POST":
        foto = request.FILES.get("foto")
        if foto is not None:
            handle_uploaded_file(foto)
            foto = f"servicios/{foto.name}"
        else:
            foto = "servicios/default.png"

        nombre_ser = request.POST.get("nombre_ser").strip()
        desc_ser = request.POST.get("desc_ser").strip()
        precio = request.POST.get("precio").strip()
        categoria = request.POST.get("categorias").strip()

        # Validaciones
        if not nombre_ser or not desc_ser or not precio or not categoria:
            messages.error(request, "Los campos no pueden estar vacíos")
            return redirect("servicios_crear")

        regex = r'^(?!.* {2})(?!.*\.\.)(?!.*\s$)[A-Za-zÁÉÍÓÚáéíóúÑñ ,.¡!¿?]*$'
        regex_precio = r'^\d+(\.\d{1,2})?$'

        if not re.match(regex, nombre_ser):
            messages.error(request, "El nombre no puede contener números ni caracteres especiales")
            return redirect("servicios_crear")

        if not re.match(regex, desc_ser):
            messages.error(request, "La descripción no puede contener números ni caracteres especiales")
            return redirect("servicios_crear")

        if not re.match(regex_precio, precio):
            messages.error(request, "El precio debe ser un número válido con hasta dos decimales")
            return redirect("servicios_crear")

        try:
            categoria = Categoria.objects.get(pk=categoria)
        except Categoria.DoesNotExist:
            messages.error(request, "La categoría seleccionada no existe")
            return redirect("servicios_crear")

        try:
            servicio = Servicio(
                nombre_ser=nombre_ser,
                desc_ser=desc_ser,
                precio=precio,
                categoria=categoria,
                foto=foto
            )
            servicio.save()
            messages.success(request, "Servicio guardado exitosamente.")
        except Exception as e:
            messages.error(request, f"Error: {e}")
        return redirect("servicios")


@require_http_methods(["GET", "POST"])
def servicios_editar(request, id_servicio):
    servicio = get_object_or_404(Servicio, id=id_servicio)
    cat = Categoria.objects.all()

    if request.method == 'GET':
        # Renderiza el formulario con los datos actuales
        return render(request, 'reparado/servicios/servicio_editar_modal.html', {'servicio': servicio,
                                                                                 'categorias': cat})
    elif request.method == 'POST':
        nombre_ser = request.POST.get('nombre_ser', '').strip()
        desc_ser = request.POST.get('desc_ser', '').strip()
        precio = request.POST.get("precio", '').strip()
        categoria = request.POST.get("categorias", '').strip()

        # Validaciones
        regex_nombre_desc = r'^(?!.* {2})(?!.*\.\.)(?!.*\s$)[A-Za-zÁÉÍÓÚáéíóúÑñ ,.¡!¿?]*$'
        regex_precio = r'^\d+(\.\d{1,2})?$'  # Permite precios en formato decimal

        if not nombre_ser or not re.match(regex_nombre_desc, nombre_ser):
            messages.error(request, "El nombre del servicio no es válido. No debe contener números ni caracteres "
                                    "especiales.")
        elif not desc_ser or not re.match(regex_nombre_desc, desc_ser):
            messages.error(request, "La descripción del servicio no es válida. No debe contener números ni caracteres "
                                    "especiales.")
        elif not precio or not re.match(regex_precio, precio):
            messages.error(request, "El precio no es válido. Debe ser un número con hasta dos decimales.")
        elif not categoria or not Categoria.objects.filter(pk=categoria).exists():
            messages.error(request, "La categoría seleccionada no es válida.")
        else:
            try:
                # Actualiza los campos del servicio
                servicio.nombre_ser = nombre_ser
                servicio.desc_ser = desc_ser
                servicio.precio = float(precio)
                servicio.categoria = Categoria.objects.get(pk=categoria)
                servicio.save()
                messages.success(request, 'Datos actualizados con éxito!!!')
                return redirect("servicios")
            except Exception as e:
                messages.error(request, f"Se produjo un error: {e}")

        return render(request, 'reparado/servicios/servicio_editar_modal.html', {'servicio': servicio,
                                                                                 'categorias': cat})


def servicios_eliminar(request, id_servicio):
    try:
        servicio = get_object_or_404(Servicio, pk=id_servicio)
        if request.method == "GET":
            return render(request, 'reparado/servicios/servicio_eliminar_modal.html', {'servicio': servicio})
        elif request.method == 'POST':
            # Procesa el formulario y actualiza la base de datos
            servicio.delete()
            messages.success(request, 'Servicio eliminado con éxito...')
            return redirect("servicios")
    except Exception as e:
        messages.error(request, f"Error: {e}")

    return redirect("servicios")


def solicitudes(request):
    # Obtener el ID del usuario registrado
    logueo = request.session.get("logueo", False)
    sesion_id = request.session.get("logueo", {}).get("id")
    if logueo:
        sol = Solicitud.objects.all()
        solicitudes_realizadas = []

        for item in sol:
            tiempo_estimado = item.servicio.tiempo_estimado
            end_time = item.fecha_hora + timedelta(minutes=tiempo_estimado)
            solicitudes_realizadas.append({
                "title": item.servicio.nombre_ser,
                "start": item.fecha_hora.strftime("%Y-%m-%d %H:%M:%S"),
                "end": end_time.strftime("%Y-%m-%d %H:%M:%S"),
            })

        if logueo["rol"] == "ADMIN":
            q = Solicitud.objects.all()
        elif logueo["rol"] == "TEC":
            q = Solicitud.objects.filter(tecnico_id=sesion_id)
        else:
            # Filtrar las solicitudes asociadas al usuario registrado
            q = Solicitud.objects.filter(usuario_id=sesion_id)

        context = {"data": q, "solicitudes": json.dumps(solicitudes_realizadas)}
        return render(request, "reparado/solicitud/solicitudes_servicios.html", context)
    else:
        messages.info(request, "No tiene permisos para acceder al módulo...")
        return redirect("index")


def solicitud_servicio(request, id_servicio):
    servicio = get_object_or_404(Servicio, id=id_servicio)
    logueo = request.session.get("logueo", False)
    tecnicos = Usuario.objects.filter(rol="TEC", categorias__in=[servicio.categoria])

    if request.method == 'GET':
        return render(request, 'reparado/solicitud/solicitud_servicio_modal.html', {
            'servicio': servicio,
            'tecnicos': tecnicos
        })

    elif request.method == 'POST':
        # Procesa el formulario y actualiza la base de datos
        servicio = get_object_or_404(Servicio, pk=request.POST.get("servicio_id"))
        fecha_hora_str = request.POST.get("fecha_hora")
        fecha_hora_str = fecha_hora_str.replace('T', ' ')
        fecha_hora = datetime.strptime(fecha_hora_str, '%Y-%m-%d %H:%M')
        precio = int(request.POST.get("precio"))
        zona = request.POST.get("zona")
        tecnico_id = request.POST.get("tecnico_id")
        tecnico = get_object_or_404(Usuario, pk=tecnico_id)
        u = get_object_or_404(Usuario, pk=logueo["id"])
        fecha_actual = timezone.now()

        if fecha_hora <= fecha_actual:
            messages.error(request, "Por favor validar que la fecha sea válida.")
            return redirect('servicios')

        tiempo_estimado = timedelta(minutes=servicio.tiempo_estimado)
        inicio = fecha_hora
        fin = fecha_hora + tiempo_estimado

        # Añadir tiempo estimado a la fecha_hora para calcular fecha_final
        solicitudes = Solicitud.objects.annotate(
            tiempo_estimado_duration=ExpressionWrapper(
                F('tiempo_estimado') * timedelta(minutes=1),
                output_field=DurationField()
            )
        ).annotate(
            fecha_final=ExpressionWrapper(
                F('fecha_hora') + F('tiempo_estimado_duration'),
                output_field=DateTimeField()
            )
        )

        # Validar conflictos de horario considerando el tiempo estimado
        conflictos = solicitudes.filter(
            tecnico=tecnico,
            fecha_hora__lt=fin,
            fecha_final__gt=inicio
        )

        if conflictos.exists():
            messages.error(request, "El técnico seleccionado no está disponible en la fecha y hora seleccionada.")
            return redirect('servicios')

        solicitud = Solicitud.objects.create(
            servicio=servicio,
            fecha_hora=fecha_hora,
            precio=precio,
            zona=zona,
            usuario=u,
            tecnico=tecnico,
            estado="PROGRAMADO"
        )

        messages.success(request, 'Cita agendada con éxito!!!')
        return redirect('servicios')


def solicitud_editar(request, id_solicitud):
    solicitud = get_object_or_404(Solicitud, id=id_solicitud)
    estados = Solicitud.ESTADOS

    if request.method == 'GET':
        # Renderiza el formulario con los datos actuales
        return render(request, 'reparado/solicitud/solicitud_editar_modal.html',
                      {'solicitud': solicitud, 'estados': estados})

    elif request.method == 'POST':
        # Procesa el formulario y actualiza la base de datos
        fecha_hora_str = request.POST.get('fecha_hora')
        fecha_hora_str = fecha_hora_str.replace('T', ' ')
        fecha_hora = datetime.strptime(fecha_hora_str, '%Y-%m-%d %H:%M')  # Convertir a objeto datetime
        zona = request.POST.get('zona')
        estado = request.POST.get("estado")
        tiempo_estimado = int(request.POST.get("tiempo"))  # Obtener tiempo estimado del formulario

        inicio = fecha_hora
        fin = fecha_hora + timedelta(minutes=tiempo_estimado)

        # Validar conflictos de horario considerando el tiempo estimado
        solicitudes = Solicitud.objects.annotate(
            fecha_final=ExpressionWrapper(F('fecha_hora') + F('tiempo_estimado') * timedelta(minutes=1),
                                          output_field=DateTimeField())
        )

        conflictos = solicitudes.filter(
            tecnico=solicitud.tecnico,
            fecha_hora__lt=fin,
            fecha_final__gt=inicio
        ).exclude(id=solicitud.id)  # Excluir la solicitud actual

        if conflictos.exists():
            messages.error(request, "Ya existe un servicio solicitado en la misma fecha y hora.")
            return redirect('solicitudes')

        # Actualizar la solicitud con los nuevos valores
        solicitud.fecha_hora = fecha_hora
        solicitud.zona = zona
        solicitud.estado = estado
        solicitud.tiempo_estimado = tiempo_estimado
        solicitud.save()

        messages.success(request, 'Datos actualizados con éxito!!!')
        return redirect("solicitudes")


def solicitud_eliminar(request, id_solicitud):
    try:
        solicitud = get_object_or_404(Solicitud, pk=id_solicitud)
        if request.method == "GET":
            return render(request, 'reparado/solicitud/solicitud_eliminar_modal.html', {'solicitud': solicitud})
        elif request.method == 'POST':
            # Procesa el formulario y actualiza la base de datos
            solicitud.delete()
            messages.success(request, 'Solicitud eliminado con éxito...')
            return redirect("solicitudes")
    except Exception as e:
        messages.error(request, f"Error: {e}")

    return redirect("solicitudes")


def usuarios(request):
    # Verificar si el usuario ha iniciado sesión
    logueo = request.session.get("logueo", False)

    if not logueo:
        # Si no ha iniciado sesión, mostrar mensaje de error y redirigir al índice
        messages.error(request, "Debe iniciar sesión...")
        return redirect("index")

    # Verificar si el usuario tiene rol de ADMIN
    if logueo.get("rol") == "ADMIN":
        # Obtener todos los usuarios
        q = Usuario.objects.all()
        # Preparar el contexto con los datos de los usuarios
        context = {"data": q}
        # Renderizar la plantilla con el contexto
        return render(request, "reparado/usuarios/usuarios_listar.html", context)
    else:
        # Si el usuario no es ADMIN, mostrar mensaje de error y redirigir al índice
        messages.error(request, "No tiene los permisos para acceder al módulo")
        return redirect("index")


@require_http_methods(["GET", "POST"])
def usuarios_crear(request):
    logueo = request.session.get("logueo", False)

    if not logueo:
        messages.error(request, "Debe iniciar sesión...")
        return redirect("index")

    if logueo["rol"] != "ADMIN":
        messages.error(request, "No tiene los permisos para acceder al módulo")
        return redirect("index")

    if request.method == "GET":
        return render(request, "reparado/usuarios/usuarios_crear.html")

    if request.method == "POST":
        foto = request.FILES.get("foto")
        if foto is not None:
            handle_uploaded_file(foto)
            foto = f"usuarios/{foto.name}"
        else:
            foto = "usuarios/default.png"

        # Extracción y saneamiento de los campos
        nombre = request.POST.get("nombre", "").strip()
        apellido = request.POST.get("apellido", "").strip()
        fecha_nacimiento = request.POST.get("fecha_nacimiento", "").strip()
        username = request.POST.get("username", "").strip()
        rol = request.POST.get("rol", "").strip()
        password = hash_password(request.POST.get("password", "")).strip()
        email = request.POST.get("email", "").strip()
        direccion = request.POST.get("direccion", "").strip()
        telefono = request.POST.get("telefono", "").strip()

        # Validaciones
        regex_nombre_apellido = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$'
        regex_username = r'^[\w.@+-]+$'  # Usar una expresión regular adecuada para usernames
        regex_email = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        regex_telefono = r'^\+?\d{9,15}$'  # Permite números de teléfono con o sin código de país

        if not nombre or not re.match(regex_nombre_apellido, nombre):
            messages.error(request, "El nombre no es válido. No debe contener números ni caracteres especiales.")
        elif not apellido or not re.match(regex_nombre_apellido, apellido):
            messages.error(request, "El apellido no es válido. No debe contener números ni caracteres especiales.")
        elif not username or not re.match(regex_username, username):
            messages.error(request, "El nombre de usuario no es válido.")
        elif not email or not re.match(regex_email, email):
            messages.error(request, "El correo electrónico no es válido.")
        elif not telefono or not re.match(regex_telefono, telefono):
            messages.error(request, "El número de teléfono no es válido.")
        elif not fecha_nacimiento:
            messages.error(request, "La fecha de nacimiento es obligatoria.")
        elif not password:
            messages.error(request, "La contraseña es obligatoria.")
        else:
            try:
                q = Usuario(
                    nombre=nombre,
                    apellido=apellido,
                    username=username,
                    password=password,
                    rol=rol,
                    fecha_nacimiento=fecha_nacimiento,
                    email=email.lower(),
                    direccion=direccion,
                    telefono=telefono,
                    foto=foto
                )
                q.save()
                messages.success(request, "Usuario guardado exitosamente.")
                return redirect("usuarios")
            except Exception as e:
                messages.error(request, f"Error: {e}")

        return render(request, "reparado/usuarios/usuarios_crear.html")

    else:
        messages.warning(request, "No se enviaron datos.")
        return redirect("usuarios_crear")


@require_GET
def usuarios_visualizar(request, id_usuario):
    logueo = request.session.get("logueo", False)
    usuario = get_object_or_404(Usuario, id=id_usuario)
    if logueo:
        if logueo["rol"] == "ADMIN":
            return render(request, 'reparado/usuarios/usuario_visualizar_modal.html', {'usuario': usuario})
        else:
            messages.warning(request, "No tiene permisos para acceder al módulo.")
            return redirect("index")
    else:
        messages.warning(request, "Debe estar logueado para ver esta información.")
        return redirect("index")


@require_GET
def visualizar_perfil(request, id_usuario):
    logueo = request.session.get("logueo", False)
    usuario = get_object_or_404(Usuario, id=id_usuario)
    if logueo:
        if logueo["id"] == id_usuario:
            return render(request, 'reparado/usuarios/usuario_perfil_modal.html', {'usuario': usuario})
        else:
            messages.warning(request, "Esta tratando de visualizar información de otro perfil.")
            return redirect("index")
    else:
        messages.warning(request, "Debe estar logueado para ver esta información.")
        return redirect("index")


@require_http_methods(["GET", "POST"])
def usuarios_editar(request, id_usuario):
    usuario = get_object_or_404(Usuario, pk=id_usuario)
    roles = usuario.ROLES
    categorias = Categoria.objects.all()
    logueo = request.session.get("logueo", False)

    if not logueo:
        messages.info(request, "Debe iniciar sesión...")
        return redirect("index")

    if request.method == 'GET':
        return render(request, 'reparado/usuarios/usuario_editar_modal.html', {'usuario': usuario,
                                                                               'roles': roles,
                                                                               'categorias': categorias})

    if logueo.get("rol") == "ADMIN" or logueo.get("id") == id_usuario:
        # Extracción y saneamiento de los campos
        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        rol = request.POST.get('rol', '').strip()
        email = request.POST.get("email", "").strip()
        fecha_nacimiento = request.POST.get("fecha_nacimiento", "").strip()
        direccion = request.POST.get("direccion", "").strip()
        telefono = request.POST.get("telefono", "").strip()
        categorias_ids = request.POST.getlist("categorias")
        # Validaciones
        regex_nombre_apellido = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$'
        regex_email = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        regex_telefono = r'^\+?\d{9,15}$'  # Permite números de teléfono con o sin código de país

        if not nombre or not re.match(regex_nombre_apellido, nombre):
            messages.error(request, "El nombre no es válido. No debe contener números ni caracteres especiales.")
        elif not apellido or not re.match(regex_nombre_apellido, apellido):
            messages.error(request, "El apellido no es válido. No debe contener números ni caracteres especiales.")
        elif not email or not re.match(regex_email, email):
            messages.error(request, "El correo electrónico no es válido.")
        elif not telefono or not re.match(regex_telefono, telefono):
            messages.error(request, "El número de teléfono no es válido.")
        elif not fecha_nacimiento:
            messages.error(request, "La fecha de nacimiento es obligatoria.")
        else:
            try:
                # Actualiza los campos del usuario
                usuario.nombre = nombre
                usuario.apellido = apellido
                usuario.rol = rol
                usuario.email = email.lower()
                usuario.fecha_nacimiento = fecha_nacimiento
                usuario.direccion = direccion
                usuario.telefono = telefono
                usuario.save()

                # Actualiza las categorías
                usuario.categorias.set(categorias_ids)

                messages.success(request, 'Datos actualizados con éxito!!!')
                return redirect("usuarios")
            except Exception as e:
                messages.error(request, f"Se produjo un error: {e}")
    else:
        messages.info(request, "No tiene permisos para realizar cambios...")
        return redirect("index")

    return render(request, 'reparado/usuarios/usuario_editar_modal.html', {'usuario': usuario})


def usuarios_eliminar(request, id_usuario):
    try:
        logueo = request.session.get("logueo", False)
        sesion_id = logueo.get("id")
        usuario = Usuario.objects.get(pk=id_usuario)

        if not logueo:
            messages.info(request, "Debe iniciar sesión...")
            return redirect("index")

        if logueo.get("rol") != "ADMIN":
            messages.info(request, "No tiene los permisos para realizar esta acción...")
            return redirect("index")

        if request.method == "GET":
            return render(request, 'reparado/usuarios/usuario_eliminar_modal.html', {'usuario': usuario})

        if request.method == 'POST':
            if sesion_id != id_usuario:
                # Procesa el formulario y actualiza la base de datos
                usuario.delete()
                messages.success(request, 'Usuario eliminado con éxito...')
                return redirect("usuarios")
            else:
                messages.success(request, 'Usuario tiene la sesión activa...')
    except Exception as e:
        messages.error(request, f"Error: {e}")
    return redirect("usuarios")


# Carro de compras

def carrito_add(request):
    if request.method == "GET":
        id_solicitud = request.GET.get("id_solicitud")

        try:
            solicitud = Solicitud.objects.get(pk=id_solicitud)
            carrito = request.session.get("carrito", [])
            item_existente = False

            for item in carrito:
                if item["id"] == id_solicitud:
                    messages.info(request, "La solicitud ya está en el carrito.")
                    item_existente = True
                    break

            if not item_existente:
                carrito.append({"id": id_solicitud, "nombre": solicitud.servicio.nombre_ser,
                                "precio": solicitud.precio,
                                "tiempo": solicitud.tiempo_estimado})
                request.session["carrito"] = carrito
                request.session["items_carrito"] = len(carrito)
                messages.success(request, "Solicitud agregada al carrito.")

            return redirect("ver_carrito")

        except Solicitud.DoesNotExist:
            messages.error(request, "La solicitud seleccionado no existe.")
            return redirect("ver_carrito")  # O redirige a donde sea necesario

    else:
        return HttpResponse("No se enviaron datos...")


def ver_carrito(request):
    carrito = request.session.get("carrito", False)
    total = 0
    solicitudes = []
    for p in carrito:
        q = Solicitud.objects.get(pk=p["id"])
        q.subtotal = q.precio * (q.tiempo_estimado / 60)
        solicitudes.append(q)
        total += int(q.subtotal)
    request.session["total_carrito"] = total
    contexto = {"data": solicitudes, "total": total}
    return render(request, "reparado/carrito/listar_carrito.html", contexto)


def eliminar_item_carrito(request, id_solicitud):
    carrito = request.session.get("carrito", False)
    for i, p in enumerate(carrito):
        if id_solicitud == int(p["id"]):
            carrito.pop(i)
            messages.info(request, "Servicio eliminado...")
            break
    else:
        messages.warning(request, "Servicio no encontrado...")

    request.session["carrito"] = carrito
    request.session["items_carrito"] = len(carrito)
    return redirect("ver_carrito")


def vaciar_carrito(request):
    carrito = request.session.get("carrito", False)
    try:
        # vaciar lista....
        carrito.clear()
        request.session["carrito"] = carrito
        request.session["items_carrito"] = 0
        messages.success(request, "Ya no hay items en el carrito!!")
    except Exception as e:
        messages.error(request, "Ocurrió un error, intente de nuevo...")

    return redirect("servicios")


@transaction.atomic
def guardar_compra(request):
    total_carrito = request.session.get("total_carrito", 0)
    logueo = request.session.get("logueo", False)

    if logueo:
        usuario = Usuario.objects.get(pk=logueo["id"])

        # Supongamos que método de pago y forma de pago se obtienen del request
        metodo_pago_seleccionado = request.POST.get("metodo_pago", "EFECTIVO")
        forma_pago_seleccionada = request.POST.get("forma_pago", "CONTADO")

        try:
            # Crear una nueva compra
            compra = Compra.objects.create(
                usuario=usuario,
                estado=1  # Estado predeterminado
            )

            # Crear la factura relacionada con la compra
            Factura.objects.create(
                compra=compra,
                total=total_carrito,
                metodo_pago=metodo_pago_seleccionado,
                forma_pago=forma_pago_seleccionada,
                fecha_pago=timezone.now()  # O el valor correcto para la fecha de pago
            )

            # Limpia el carrito
            request.session["carrito"] = []
            request.session["items_carrito"] = 0
            messages.success(request, "Compra y factura guardadas correctamente.")
            return redirect('detalle_compra', compra_id=compra.id)
        except Exception as e:
            transaction.set_rollback(True)
            messages.error(request, f"Error al guardar la compra: {e}")
    else:
        messages.error(request, "Usuario no autenticado.")

    return redirect("inicio")


def detalle_compra(request, compra_id):
    compra = get_object_or_404(Compra, pk=compra_id)
    factura = get_object_or_404(Factura, compra=compra)
    contexto = {
        'compra': compra,
        'factura': factura
    }
    return render(request, 'reparado/carrito/detalle_compra.html', contexto)


def detalle_compras(request):
    logueo = request.session.get("logueo", False)

    if logueo:
        usuario_id = logueo["id"]
        compras = Compra.objects.filter(usuario_id=usuario_id)
        facturas = Factura.objects.filter(compra__usuario_id=usuario_id)

        contexto = {
            'compras': compras,
            'facturas': facturas
        }
        return render(request, 'reparado/carrito/detalle_compras.html', contexto)
    else:
        return redirect('index')


def enviar_correo(ruta, email, token):
    destinatario = email
    mensaje = f"""
    		<h1 style='color:blue;'>Inventario</h1>
    		<p>Usted realizó una solicitud de cambio de clave.</p>
    		<p>Haga click aquí:</p>
    		<br>
    		<a href='http://127.0.0.1:8000/{ruta}'>Recuperar contraseña </a>
    		<br>
    		<p>Digite el siguiente token: <strong>{token}</strong></p>
    		"""

    try:
        msg = EmailMessage("Tienda ADSO", mensaje, settings.EMAIL_HOST_USER, [destinatario])
        msg.content_subtype = "html"  # Habilitar contenido html
        msg.send()
        return "Correo enviado"
    except BadHeaderError:
        return "Encabezado no válido"
    except Exception as e:
        return f"Error: {e}"


# ------------------------------- Para los permisos de los end-points -----------------------------



# Vistas para API

class UsuarioViewSet(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication, SessionAuthentication]
    # authentication_classes = [TokenAuthentication]
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer


class CategoriaViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated]
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer


class ServicioViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated]
    queryset = Servicio.objects.all()
    serializer_class = ServicioSerializer


class SolicitudViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated]
    queryset = Solicitud.objects.all()
    print(queryset)
    serializer_class = SolicitudSerializer



class ComentarioViewSet(viewsets.ModelViewSet):
    queryset = Comentario.objects.all()
    serializer_class = ComentarioSerializer


"""class AuditoriaViewSet(viewsets.ModelViewSet):
    queryset = Auditoria.objects.all()
    serializer_class = AuditoriaSerializer"""


class FacturaViewSet(viewsets.ModelViewSet):
    queryset = Factura.objects.all()
    serializer_class = FacturaSerializer


"""class MetodoPagoViewSet(viewsets.ModelViewSet):
    queryset = MetodoPago.objects.all()
    serializer_class = MetodoPagoSerializer"""

"""class FacturaPagoViewSet(viewsets.ModelViewSet):
    queryset = FacturaPago.objects.all()
    serializer_class = FacturaPagoSerializer"""


class ServicioFiltroCategoria(generics.ListAPIView):
    serializer_class = ServicioSerializer

    def get_queryset(self):
        # Vista para mostrar todos los productos de una categoría específica.
        cat = self.kwargs['categorias']
        # tema_obj = Tema.objects.get(pk=tema)
        return Servicio.objects.filter(categoria=cat).order_by('-nombre_ser')
    
class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        
        
        print(request.data)

        serializer = UserSerializer(data=request.data)
        print(serializer)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Usuario registrado exitosamente"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


"""-------------------Personalización de Token de Autenticación----------------------------"""


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['username']
        # traer datos del usuario para bienvenida y ROL
        usuario = Usuario.objects.get(username=user)
        token, created = Token.objects.get_or_create(user=usuario)

        return Response({
            'token': token.key,
            'user': {
                'user_id': usuario.pk,
                'email': usuario.email,
                'nombre': usuario.nombre,
                'apellido': usuario.apellido,
                'rol': usuario.rol,
                'foto': usuario.foto.url
            }

        })

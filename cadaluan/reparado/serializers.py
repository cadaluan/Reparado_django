from .models import *
from rest_framework import serializers


class UsuarioSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Usuario
        fields = ['id', 'nombre', 'apellido', 'email', 'direccion', 'foto']

        # fields = '__all__'


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        # fields = ['id', 'nombre', 'apellido', 'email', 'direccion']
        fields = '__all__'


class ServicioSerializer(serializers.ModelSerializer):
    # Campos con relaciones, para traer dato específico
    categoria_name = serializers.StringRelatedField(many=False, source='categoria.nombre_cat')

    class Meta:
        model = Servicio
        fields = ['id', 'nombre_ser', 'desc_ser', 'precio', 'categoria', 'categoria_name', 'foto']
        #  fields = '__all__'


class SolicitudSerializer(serializers.ModelSerializer):
     # Campos con relaciones, para traer dato específico
    servicio_name = serializers.StringRelatedField(many=False, source='servicio.nombre_ser')
    usuario_name = serializers.StringRelatedField(many=False, source='usuario.nombre')
    class Meta:
        model = Solicitud
        fields = ['id','usuario_name','servicio_name', 'fecha_hora', 'precio', 'tiempo_estimado', 'zona', 'usuario', 'tecnico', 'estado' ]
        #fields = '__all__'


class ComentarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comentario
        fields = ['id_solicitud', 'estado', 'comentario']
        # fields = '__all__'


class FacturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Factura
        # fields = ['id_solicitud', 'estado', 'comentario']
        fields = '__all__'


"""class MetodoPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetodoPago
        # fields = ['id_solicitud', 'estado', 'comentario']
        fields = '__all__'"""


"""class FacturaPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacturaPago
        # fields = ['id_solicitud', 'estado', 'comentario']
        fields = '__all__'"""


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'rol']


class UserSerializer(serializers.ModelSerializer):
   # password = serializers.CharField(write_only=True)

    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    

    class Meta:
        model = Usuario
        fields = ['username', 'password']

    def create(self, validated_data):
        user = Usuario(
            username=validated_data['username'],
            
        )
        user.set_password(validated_data['password'])  # Encripta la contraseña
        user.save()
        return user
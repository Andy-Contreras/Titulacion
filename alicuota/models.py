from django.core.exceptions import ValidationError
from django.db import models
from main import settings
from alicuota.util import *
from django.contrib.auth.models import User

# Tabla audutoria
class AuditUser(models.Model):
    TIPOS_ACCIONES = (
        ('A', 'A'),  # Adicion
        ('M', 'M'),  # Modificacion
        ('E', 'E')  # Eliminacion
    )
    usuario = models.ForeignKey(User, verbose_name='Usuario', on_delete=models.PROTECT)
    tabla = models.CharField(max_length=100, verbose_name='Tabla')
    registroid = models.IntegerField(verbose_name='Registro Id')
    accion = models.CharField(choices=TIPOS_ACCIONES, max_length=10, verbose_name='Accion')
    fecha = models.DateField(verbose_name='Fecha')
    hora = models.TimeField(verbose_name='Hora')
    estacion = models.CharField(max_length=100, verbose_name='Estacion')

    def _str_(self):
        return "{} - {} [{}]".format(self.usuario.username, self.tabla, self.accion)

    class Meta:
        verbose_name = 'Auditoria Usuario '
        verbose_name_plural = 'Auditorias Usuarios'
        ordering = ('-fecha', 'hora')

# Modelo Para vehiculo---------------------------------------------------------------------------
class Marca(models.Model):
    nombre_marca = models.CharField(
        max_length=50, verbose_name="Nombre de la Marca",
        blank=False, null=False, unique=True
    )

    def __str__(self):
        return self.nombre_marca


class Modelo(models.Model):
    nombre_modelo = models.CharField(
        max_length=50, verbose_name="Nombre del Modelo",
        blank=False, null=False, unique=True
    )
    marca = models.ForeignKey(
        Marca, on_delete=models.CASCADE,
        verbose_name="Marca",
        related_name='modelos',
        blank=False, null=False
    )

    def __str__(self):
        return f"{self.nombre_modelo} - {self.marca}"


class Vehiculo(models.Model):
    modelo = models.ForeignKey(
        Modelo, on_delete=models.CASCADE,
        verbose_name="Modelo",
        related_name='vehiculos',
        blank=False, null=False
    )
    placa = models.CharField(
        max_length=50, verbose_name="Placa",
        blank=False, null=False, unique=True
    )
    anio = models.PositiveIntegerField(
        verbose_name="Año",
        blank=False, null=False
    )
    color = models.CharField(
        max_length=50, verbose_name="Color",
        blank=False, null=False
    )
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.placa} - {self.modelo}"


# Modelo de TipoResidente----------------------------------------------------------------
class TipoResidente(models.Model):
    descripcion = models.CharField(
        max_length=50,
        verbose_name="Descripción",
        blank=False,
        null=False
    )

    def __str__(self):
        return self.descripcion


# Modelo Residente ---------------------------------------------------------------------------------

class Residente(models.Model):
    tipo_residente = models.ForeignKey(
        TipoResidente, on_delete=models.CASCADE,
        verbose_name="Tipo Residente",
        related_name='residentes',
        blank=False,
        null=False
    )
    vehiculo = models.OneToOneField(
        Vehiculo, on_delete=models.SET_NULL,
        verbose_name="Vehículo",
        null=True,
        blank=True,
        related_name='residentes'
    )
    nombre = models.CharField(
        max_length=50,
        verbose_name="Nombre Residente",
        blank=False,
        null=False
    )
    telefono = models.CharField(
        max_length=10,
        verbose_name="Teléfono",
        blank=False,
        null=False, unique=True, validators=[solo_numeros_validator]
    )
    email = models.EmailField(
        max_length=50,
        verbose_name="Email",
        blank=False,
        null=False, unique=True
    )
    cedula = models.CharField(
        max_length=13,
        verbose_name="Cédula",
        blank=False,
        null=False, unique=True, validators=[validar_cedula_ecuatoriana, solo_numeros_validator],
    )
    activo = models.BooleanField(default=True)
    # Nuevo campo status para indicar si es residente o cliente
    status = models.BooleanField(
        default=True,  # True indica que es residente, False indica que es cliente
        verbose_name="Estado",
    )

    def get_status_display(self):
        return "Residente" if self.status else "Cliente"

    def __str__(self):
        return self.nombre


# Modelo Urbanizacion
class Urbanizacion(models.Model):
    nombre_urbanizacion = models.CharField(max_length=50, blank=False, null=False, unique=True)
    direccion = models.CharField(max_length=50, blank=False, null=False)

    def __str__(self):
        return self.nombre_urbanizacion

    class Meta:
        verbose_name = "Urbanización"
        verbose_name_plural = "Urbanizaciones"


# Modelo de Manzana
class Manzana(models.Model):
    urbanizacion = models.ForeignKey(Urbanizacion, on_delete=models.CASCADE, blank=False,
                                     null=False)
    codigo_manzana = models.CharField(max_length=50, blank=False, null=False)

    def __str__(self):
        return self.codigo_manzana


# Modelo de Villa
class Villa(models.Model):
    manzana = models.ForeignKey(Manzana, on_delete=models.CASCADE, blank=False,
                                null=False)
    numero_villa = models.CharField(max_length=50, blank=False, null=False, unique=True)

    def __str__(self):
        return f'{self.manzana.codigo_manzana} - {self.numero_villa}'


# Modeo Tipo Vivienda
class TipoVivienda(models.Model):
    descripcion = models.CharField(max_length=50, blank=False, null=False)

    def __str__(self):
        return self.descripcion


# Modelo Tasa de Interez
class TasaInterez(models.Model):
    porcentaje = models.IntegerField()

    def clean(self):
        if self.porcentaje < 0 or self.porcentaje > 99:
            raise ValidationError('El porcentaje debe estar entre 0 y 99.')

    def __str__(self):
        return f"{self.porcentaje}%"

    class Meta:
        verbose_name = "Tasa de interés"
        verbose_name_plural = "Tasas de interés"


# Modelo Tasa de Entrada
class TasaEntrada(models.Model):
    porcentaje = models.IntegerField()

    def clean(self):
        if self.porcentaje < 0 or self.porcentaje > 99:
            raise ValidationError('El porcentaje debe estar entre 0 y 99.')

    def __str__(self):
        return f"{self.porcentaje}%"
# Modelo Vivienda
class Vivienda(models.Model):
    tipovivienda = models.ForeignKey(TipoVivienda, on_delete=models.CASCADE, blank=False, null=False)
    residente = models.ForeignKey('Residente', on_delete=models.CASCADE, blank=True, null=True)
    villa = models.OneToOneField(Villa, on_delete=models.CASCADE, blank=False, null=False, unique=True)
    descripcion = models.CharField(max_length=50, blank=False, null=False)
    habitaciones = models.IntegerField(blank=False, null=False)
    banos = models.IntegerField(blank=False, null=False)
    valor = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False)
    metros_cuadrados = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False)
    imagen = models.FileField(upload_to='logo/vivienda', blank=True, null=True)
    estado = models.BooleanField(default=True, help_text="Estado de disponibilidad de la vivienda")

    def __str__(self):
        if self.residente:
            return f"{self.descripcion} - {self.residente.nombre}"
        return f"{self.descripcion} - Sin residente"

    def get_image(self):
        if self.imagen:
            return f"{settings.MEDIA_URL}{self.imagen}"
        return f"{settings.STATIC_URL}img/empty.jpg"

    def estado_display(self):
        return "Ocupada" if self.estado else "Disponible"


# Model familia residente
class FamiliaPropietario(models.Model):
    residente = models.ForeignKey(Residente, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=50, blank=False, null=False)

    def __str__(self):
        return f"Familia de {self.residente}"


class MiembroFamilia(models.Model):
    familia = models.ForeignKey(FamiliaPropietario, on_delete=models.CASCADE, related_name="miembros")
    nombre = models.CharField(max_length=50, blank=False, null=False)
    cedula = models.CharField(max_length=10, unique=True, null=False, blank=False)
    sexo = models.CharField(max_length=50, blank=False, null=False)
    fecha_nacimiento = models.DateField(blank=False, null=False)
    parentesco = models.CharField(max_length=50, blank=False, null=False)

    def __str__(self):
        return f"{self.nombre} ({self.parentesco})"


# Modeo Alicuota - Cabecera de la alicuota
class CabAlicuota(models.Model):
    vivienda = models.ForeignKey(Vivienda, on_delete=models.CASCADE)
    Interes = models.ForeignKey(TasaInterez, on_delete=models.CASCADE)
    entrada_tasa = models.ForeignKey(TasaEntrada, on_delete=models.CASCADE)
    pago_inicial = models.DecimalField(max_digits=10, decimal_places=2)
    saldo_pagar = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_creacion = models.DateField()
    fecha_pago =models.DateField()
    periodo = models.IntegerField()  # Las letras que se van a diferir en la alicuota
    monto = models.DecimalField(max_digits=10, decimal_places=2)  # Monto que se trae de la vivienda
    saldo_financiar = models.DecimalField(max_digits=10, decimal_places=2)
    saldo_pendiente = models.DecimalField(max_digits=10,
                                          decimal_places=2, null= True)  # Saldo Pendiente de las letras que se van cancelando
    Interestotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.nombre} ({self.monto})({self.tasa_interez})({self.periodo})"

# Detalle alicuota
class DetAlicuota(models.Model):
    cab_alicuota = models.ForeignKey(CabAlicuota, on_delete=models.CASCADE)
    secuencia = models.IntegerField()
    fecha = models.DateField()
    fecha_vencimiento = models.DateField()
    recargo = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    saldo_pagar = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=10)

# Pago
class CabFactura(models.Model):
    id_residentes = models.ForeignKey('Residente', on_delete=models.CASCADE)
    id_cabalicuotra = models.ForeignKey('CabAlicuota', on_delete=models.CASCADE)
    fecha_creacion = models.DateField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    factura = models.IntegerField()

    def __str__(self):
        return f"Factura {self.factura} - Residente {self.id_residentes}"

class DetFactura(models.Model):
    id_cabfactura = models.ForeignKey(CabFactura, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=50)  # Este campo puede almacenar "Agosto/2024"
    valor_pagar = models.DecimalField(max_digits=10, decimal_places=2)
    recargo = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    pago = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Detalle factura {self.id_cabfactura.factura} - {self.descripcion}"



# Generar PDF PARA Alicuota
# class ReportePDF(models.Model):
#     residente = models.ForeignKey(Residente, on_delete=models.CASCADE)  # Relacionado con el residente
#     fecha_creacion = models.DateTimeField(auto_now_add=True)
#     archivo_base64 = models.TextField(null=True, blank=True)
#
#     def __str__(self):
#         return f'Reporte PDF para {self.residente.nombre}'


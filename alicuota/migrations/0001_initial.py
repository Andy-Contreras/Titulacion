# Generated by Django 4.2.16 on 2024-11-30 02:17

import alicuota.util
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CabAlicuota',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pago_inicial', models.DecimalField(decimal_places=2, max_digits=10)),
                ('saldo_pagar', models.DecimalField(decimal_places=2, max_digits=10)),
                ('fecha_creacion', models.DateField()),
                ('fecha_pago', models.DateField()),
                ('periodo', models.IntegerField()),
                ('monto', models.DecimalField(decimal_places=2, max_digits=10)),
                ('saldo_financiar', models.DecimalField(decimal_places=2, max_digits=10)),
                ('saldo_pendiente', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('Interestotal', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='CabFactura',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateField()),
                ('monto', models.DecimalField(decimal_places=2, max_digits=10)),
                ('factura', models.IntegerField()),
                ('id_cabalicuotra', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='alicuota.cabalicuota')),
            ],
        ),
        migrations.CreateModel(
            name='FamiliaPropietario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Manzana',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo_manzana', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Marca',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_marca', models.CharField(max_length=50, unique=True, verbose_name='Nombre de la Marca')),
            ],
        ),
        migrations.CreateModel(
            name='Modelo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_modelo', models.CharField(max_length=50, unique=True, verbose_name='Nombre del Modelo')),
                ('marca', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='modelos', to='alicuota.marca', verbose_name='Marca')),
            ],
        ),
        migrations.CreateModel(
            name='Residente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50, verbose_name='Nombre Residente')),
                ('telefono', models.CharField(max_length=10, unique=True, validators=[django.core.validators.RegexValidator(message='El número debe tener exactamente 10 dígitos numéricos.', regex='^\\d{10}$|^\\d{13}$')], verbose_name='Teléfono')),
                ('email', models.EmailField(max_length=50, unique=True, verbose_name='Email')),
                ('cedula', models.CharField(max_length=13, unique=True, validators=[alicuota.util.validar_cedula_ecuatoriana, django.core.validators.RegexValidator(message='El número debe tener exactamente 10 dígitos numéricos.', regex='^\\d{10}$|^\\d{13}$')], verbose_name='Cédula')),
                ('activo', models.BooleanField(default=True)),
                ('status', models.BooleanField(default=True, verbose_name='Estado')),
            ],
        ),
        migrations.CreateModel(
            name='TasaEntrada',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('porcentaje', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='TasaInterez',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('porcentaje', models.IntegerField()),
            ],
            options={
                'verbose_name': 'Tasa de interés',
                'verbose_name_plural': 'Tasas de interés',
            },
        ),
        migrations.CreateModel(
            name='TipoResidente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.CharField(max_length=50, verbose_name='Descripción')),
            ],
        ),
        migrations.CreateModel(
            name='TipoVivienda',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Urbanizacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_urbanizacion', models.CharField(max_length=50, unique=True)),
                ('direccion', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name': 'Urbanización',
                'verbose_name_plural': 'Urbanizaciones',
            },
        ),
        migrations.CreateModel(
            name='Villa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_villa', models.CharField(max_length=50, unique=True)),
                ('manzana', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='alicuota.manzana')),
            ],
        ),
        migrations.CreateModel(
            name='Vivienda',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.CharField(max_length=50)),
                ('habitaciones', models.IntegerField()),
                ('banos', models.IntegerField()),
                ('valor', models.DecimalField(decimal_places=2, max_digits=10)),
                ('metros_cuadrados', models.DecimalField(decimal_places=2, max_digits=10)),
                ('imagen', models.FileField(blank=True, null=True, upload_to='logo/vivienda')),
                ('estado', models.BooleanField(default=True, help_text='Estado de disponibilidad de la vivienda')),
                ('residente', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='alicuota.residente')),
                ('tipovivienda', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='alicuota.tipovivienda')),
                ('villa', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='alicuota.villa')),
            ],
        ),
        migrations.CreateModel(
            name='Vehiculo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('placa', models.CharField(max_length=50, unique=True, verbose_name='Placa')),
                ('anio', models.PositiveIntegerField(verbose_name='Año')),
                ('color', models.CharField(max_length=50, verbose_name='Color')),
                ('activo', models.BooleanField(default=True)),
                ('modelo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vehiculos', to='alicuota.modelo', verbose_name='Modelo')),
            ],
        ),
        migrations.AddField(
            model_name='residente',
            name='tipo_residente',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='residentes', to='alicuota.tiporesidente', verbose_name='Tipo Residente'),
        ),
        migrations.AddField(
            model_name='residente',
            name='vehiculo',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='residentes', to='alicuota.vehiculo', verbose_name='Vehículo'),
        ),
        migrations.CreateModel(
            name='MiembroFamilia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
                ('cedula', models.CharField(max_length=10, unique=True)),
                ('sexo', models.CharField(max_length=50)),
                ('fecha_nacimiento', models.DateField()),
                ('parentesco', models.CharField(max_length=50)),
                ('familia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='miembros', to='alicuota.familiapropietario')),
            ],
        ),
        migrations.AddField(
            model_name='manzana',
            name='urbanizacion',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='alicuota.urbanizacion'),
        ),
        migrations.AddField(
            model_name='familiapropietario',
            name='residente',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='alicuota.residente'),
        ),
        migrations.CreateModel(
            name='DetFactura',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.CharField(max_length=50)),
                ('valor_pagar', models.DecimalField(decimal_places=2, max_digits=10)),
                ('recargo', models.DecimalField(decimal_places=2, max_digits=10)),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=10)),
                ('pago', models.DecimalField(decimal_places=2, max_digits=10)),
                ('id_cabfactura', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='alicuota.cabfactura')),
            ],
        ),
        migrations.CreateModel(
            name='DetAlicuota',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('secuencia', models.IntegerField()),
                ('fecha', models.DateField()),
                ('fecha_vencimiento', models.DateField()),
                ('recargo', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('saldo_pagar', models.DecimalField(decimal_places=2, max_digits=10)),
                ('estado', models.CharField(max_length=10)),
                ('cab_alicuota', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='alicuota.cabalicuota')),
            ],
        ),
        migrations.AddField(
            model_name='cabfactura',
            name='id_residentes',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='alicuota.residente'),
        ),
        migrations.AddField(
            model_name='cabalicuota',
            name='Interes',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='alicuota.tasainterez'),
        ),
        migrations.AddField(
            model_name='cabalicuota',
            name='entrada_tasa',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='alicuota.tasaentrada'),
        ),
        migrations.AddField(
            model_name='cabalicuota',
            name='vivienda',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='alicuota.vivienda'),
        ),
        migrations.CreateModel(
            name='AuditUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tabla', models.CharField(max_length=100, verbose_name='Tabla')),
                ('registroid', models.IntegerField(verbose_name='Registro Id')),
                ('accion', models.CharField(choices=[('A', 'A'), ('M', 'M'), ('E', 'E')], max_length=10, verbose_name='Accion')),
                ('fecha', models.DateField(verbose_name='Fecha')),
                ('hora', models.TimeField(verbose_name='Hora')),
                ('estacion', models.CharField(max_length=100, verbose_name='Estacion')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Usuario')),
            ],
            options={
                'verbose_name': 'Auditoria Usuario ',
                'verbose_name_plural': 'Auditorias Usuarios',
                'ordering': ('-fecha', 'hora'),
            },
        ),
    ]
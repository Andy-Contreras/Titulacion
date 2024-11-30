from django import forms
from alicuota.models import *
from django.forms import modelformset_factory, inlineformset_factory
import re


# Formulario Cliente----------------------------------------------------------------------------
# class ClienteForm(forms.ModelForm):
#     class Meta:
#         model = Cliente
#         fields = ['nombre', 'cedula', 'email', 'telefono', 'direccion']
#         widgets = {
#             'nombre': forms.TextInput(attrs={
#                 'class': 'w-full border border-gray-300 p-2 rounded-md',
#                 'placeholder': 'Ingrese su nombre'
#             }),
#             'cedula': forms.TextInput(attrs={
#                 'class': 'w-full border border-gray-300 p-2 rounded-md',
#                 'placeholder': 'Ingrese su cédula'
#             }),
#             'email': forms.EmailInput(attrs={
#                 'class': 'w-full border border-gray-300 p-2 rounded-md',
#                 'placeholder': 'Ingrese su correo'
#             }),
#             'telefono': forms.TextInput(attrs={
#                 'class': 'w-full border border-gray-300 p-2 rounded-md',
#                 'placeholder': 'Ingrese su teléfono'
#             }),
#             'direccion': forms.TextInput(attrs={
#                 'class': 'w-full border border-gray-300 p-2 rounded-md',
#                 'placeholder': 'Ingrese su dirección'
#             }),
#         }
#
#     def clean_telefono(self):
#         telefono = self.cleaned_data.get('telefono')
#         if not re.match(r'^\d+$', telefono):
#             raise forms.ValidationError('El teléfono debe contener solo números.')
#         return telefono


# Formulario Vehiculo -------------------------------------------------------------------------
class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = ['modelo', 'placa', 'anio', 'color']
        widgets = {
            'modelo': forms.Select(attrs={
                'class': 'w-full border border-gray-300 p-2 rounded-md',
                'placeholder': 'Seleccione el Modelo'
            }),
            'placa': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 p-2 rounded-md',
                'placeholder': 'Ingrese la Placa'
            }),
            'anio': forms.NumberInput(attrs={
                'class': 'w-full border border-gray-300 p-2 rounded-md',
                'placeholder': 'Ingrese el Año'
            }),
            'color': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 p-2 rounded-md',
                'placeholder': 'Ingrese el color'
            }),

        }


# Formulario Residente-------------------------------------------------------------------------
class ResidenteForm(forms.ModelForm):
    class Meta:
        model = Residente
        fields = ['tipo_residente', 'vehiculo', 'nombre', 'telefono', 'email', 'cedula', 'status']  # Agregar 'status'
        widgets = {
            'tipo_residente': forms.Select(attrs={
                'class': 'w-full border border-gray-300 p-2 rounded-md',
                'placeholder': 'Seleccione el Tipo de Residente'
            }),
            'vehiculo': forms.Select(attrs={
                'class': 'w-full border border-gray-300 p-2 rounded-md',
                'placeholder': 'Seleccione el Vehículo'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 p-2 rounded-md',
                'placeholder': 'Ingrese el Nombre'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 p-2 rounded-md',
                'placeholder': 'Ingrese el Teléfono',
                'oninput': 'validarNumero(this)',  # Agregar evento para validación
                'maxlength': '10',  # Limitar a 10 caracteres
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full border border-gray-300 p-2 rounded-md',
                'placeholder': 'Ingrese el Correo Electrónico'
            }),
            'cedula': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 p-2 rounded-md',
                'placeholder': 'Ingrese la Cédula',
                'oninput': 'validarNumero(this)',  # Agregar evento para validación
                'maxlength': '10',  # Limitar a 10 caracteres
            }),
            'status': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-5 w-5 text-blue-600',
            }),
        }

# Formulario Vivienda-------------------------------------------------------------------------
class ViviendaForm(forms.ModelForm):
    class Meta:
        model = Vivienda
        fields = [
            'tipovivienda', 'residente', 'villa', 'descripcion',
            'habitaciones', 'banos', 'valor', 'metros_cuadrados', 'imagen', 'estado'
        ]
        widgets = {
            'tipovivienda': forms.Select(attrs={
                'class': 'w-full border border-gray-300 p-2 rounded-md',
                'placeholder': 'Selecciona el tipo de vivienda',
            }),
            'residente': forms.Select(attrs={
                'class': 'w-full border border-gray-300 p-2 rounded-md',
                'placeholder': 'Selecciona el residente (opcional)',
            }),
            'villa': forms.Select(attrs={
                'class': 'w-full border border-gray-300 p-2 rounded-md',
                'placeholder': 'Selecciona la villa',
            }),
            'descripcion': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 p-2 rounded-md',
            }),
            'habitaciones': forms.NumberInput(attrs={
                'class': 'w-full border border-gray-300 p-2 rounded-md',
            }),
            'banos': forms.NumberInput(attrs={
                'class': 'w-full border border-gray-300 p-2 rounded-md',
            }),
            'valor': forms.NumberInput(attrs={
                'class': 'w-full border border-gray-300 p-2 rounded-md',
                'step': '0.01',
            }),
            'metros_cuadrados': forms.NumberInput(attrs={
                'class': 'w-full border border-gray-300 p-2 rounded-md',
                'step': '0.01',
            }),
            'imagen': forms.FileInput(attrs={
                'class': 'hidden',
                'accept': 'image/*',
                'id': 'file-input',
                'onchange': 'previewImage(event)',
            }),
            'estado': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-5 w-5 text-blue-600',

            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtra residentes con status=True
        self.fields['residente'].queryset = Residente.objects.filter(status=True)


# Forms Familia Residente
class FamiliaPropietarioForm(forms.ModelForm):
    class Meta:
        model = FamiliaPropietario
        fields = ['residente', 'descripcion']
        widgets = {
            'residente': forms.Select(attrs={
                'class': 'w-full border border-gray-300 p-2 rounded-md',
            }),
            'descripcion': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 p-2 rounded-md',
                'placeholder': 'Descripción de la familia',
            }),
        }


class MiembroFamiliaForm(forms.ModelForm):
    class Meta:
        model = MiembroFamilia
        fields = ['nombre', 'cedula', 'sexo', 'fecha_nacimiento', 'parentesco']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 p-2 rounded-md',
            }),
            'cedula': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 p-2 rounded-md',
            }),
            'sexo': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 p-2 rounded-md',
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'class': 'w-full border border-gray-300 p-2 rounded-md',
                'type': 'date',
            }, format='%Y-%m-%d'),
            'parentesco': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 p-2 rounded-md',
            }),
        }
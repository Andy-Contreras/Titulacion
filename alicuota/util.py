from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models


def save_audit(request, model, action):
    from alicuota.models import AuditUser
    from django.utils import timezone
    user = request.user
    # Obtain client ip address
    client_address = ip_client_address(request)
    if model.id is None:
        raise ValueError("El objeto no tiene un ID asignado.")
    # Registro en tabla Auditora BD
    auditusuariotabla = AuditUser(usuario=user,
                                  tabla=model._meta.model_name,
                                  registroid=model.id,
                                  accion=action,
                                  fecha=timezone.now().date(),
                                  hora=timezone.now().time(),
                                  estacion=client_address)
    auditusuariotabla.save()


# Obtener el IP desde donde se esta accediendo
def ip_client_address(request):
    try:
        # case server externo
        client_address = request.META['HTTP_X_FORWARDED_FOR']
    except:
        # case localhost o 127.0.0.1
        client_address = request.META['REMOTE_ADDR']
    return client_address


# Validacion de cedula
def validar_cedula_ecuatoriana(cedula):
    """
    Valida que el valor ingresado sea una cédula (10 dígitos) o un RUC (13 dígitos) válido.
    """
    if not cedula.isdigit():
        raise ValidationError("La identificación debe contener únicamente dígitos numéricos.")

    if len(cedula) == 10:
        # Validar como cédula ecuatoriana
        provincia = int(cedula[0:2])
        if provincia < 1 or provincia > 24:
            raise ValidationError("Los dos primeros dígitos de la cédula no corresponden a una provincia válida.")

        digito_verificador = int(cedula[-1])
        suma = 0

        for i in range(9):
            digito = int(cedula[i])
            if i % 2 == 0:  # Posición par
                digito *= 2
                if digito > 9:
                    digito -= 9
            suma += digito

        suma = suma % 10
        if suma != 0:
            suma = 10 - suma

        if suma != digito_verificador:
            raise ValidationError("La cédula no es válida.")

    elif len(cedula) == 13:
        # Validar como RUC ecuatoriano
        cedulas = cedula[:10]
        validar_cedula_ecuatoriana(cedulas)  # Reutilizamos la validación de cédula.
        if cedula[10:] != "001":
            raise ValidationError("El RUC no tiene un código válido (debe terminar en '001').")

    else:
        # Si no es de longitud 10 o 13, genera un error.
        raise ValidationError("La identificación debe tener 10 dígitos (cédula) o 13 dígitos (RUC).")


# Validacion para solo numero
solo_numeros_validator = RegexValidator(
    regex=r'^\d{10}$|^\d{13}$',
    message='El número debe tener exactamente 10 dígitos numéricos.'
)


# Validaciones para las apis
def validar_cedula_ecuatoriana_api(cedula):
    try:
        if len(cedula) != 10 or not cedula.isdigit():
            print('La cédula debe tener 10 dígitos numéricos.')
            return False  # La cédula debe tener 10 dígitos numéricos.

        provincia = int(cedula[0:2])
        if provincia < 1 or provincia > 24:
            print('Los dos primeros dígitos de la cédula no corresponden a una provincia válida.')
            return False  # Los dos primeros dígitos de la cédula no corresponden a una provincia válida.

        digito_verificador = int(cedula[-1])
        suma = 0

        for i in range(9):
            digito = int(cedula[i])
            if i % 2 == 0:  # Posición par
                digito *= 2
                if digito > 9:
                    digito -= 9
            suma += digito

        suma = suma % 10
        if suma != 0:
            suma = 10 - suma

        if suma != digito_verificador:
            print('La cédula no es válida.')

            return False  # La cédula no es válida.
        print('La cédula es válida.')
        return True  # La cédula es válida.
    except (ValueError, IndexError):
        print('Captura errores de conversión y de acceso a índices.')
        return False  # Captura errores de conversión y de acceso a índices.

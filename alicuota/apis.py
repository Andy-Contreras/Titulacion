from alicuota.models import Residente,FamiliaPropietario, MiembroFamilia, CabAlicuota, AuditUser, Residente, DetAlicuota
from django.db import connection
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from alicuota.util import validar_cedula_ecuatoriana_api
from django.utils import timezone
from django.http import HttpResponse
from rest_framework.views import APIView


class ValidacionesPersonaFamiliaView(APIView):
    def post(self, request):
        try:
            persona = request.data.get('persona')
            cedula = persona['cedula']
            print(cedula)
            cedula_residente= Residente.objects.filter(cedula=cedula).exists()
            cedulaUnica = MiembroFamilia.objects.filter(cedula=cedula).exists()
            print(cedulaUnica)
            if not cedulaUnica and not cedula_residente:
                print("La cédula es única.")
                estado_cedula = validar_cedula_ecuatoriana_api(cedula)
                if estado_cedula:
                    print('La cedula es ecuatoriana')
                    return Response({'mensaje': 'La cedula es ecuatoriana'}, status=status.HTTP_200_OK)
                else:
                    print('La cedula no ecuatoriana')
                    return Response({'mensaje': 'La cedula no es ecuatoriana'}, status=status.HTTP_200_OK)
            else:
                print("La cédula ya está en uso.")
                return Response({'mensaje': 'La cédula ya está en uso.'}, status=status.HTTP_200_OK)


        except Exception as e:
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CrearFamiliaView(APIView):
    def post(self, request):
        try:
            # Obtener la IP del cliente
            ip_cliente = request.META.get('REMOTE_ADDR', '')

            residente = request.data.get('residente')
            listaFamilia = request.data.get('listaFamilia')
            print(f'Residente: {residente}')
            print(f'listaFamilia: {listaFamilia}')

            id_residente = int(residente['id'])
            with connection.cursor() as cursor:
                cursor.execute("insert into alicuota_familiapropietario(residente_id, descripcion) values(%s, %s)",
                               [id_residente, residente['descripcion']])
                print('Cabecera Creada')
                # Crear registro de auditoría para la creación de la cabecera
                AuditUser.objects.create(
                    usuario=request.user,
                    tabla="alicuota_familiapropietario",
                    registroid=id_residente,
                    accion='A',
                    fecha=timezone.now().date(),
                    hora=timezone.now().time(),
                    estacion=ip_cliente  # Cambia "Estación A" por el valor correcto de la estación
                )

            ultimoId = FamiliaPropietario.objects.latest('id').id

            for miembro in listaFamilia:
                fecha_str = miembro['fechaNacimiento']
                fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
                with connection.cursor() as cursor:
                    cursor.execute("insert into alicuota_miembrofamilia(nombre, cedula, sexo, parentesco, "
                                   "fecha_nacimiento, familia_id) values (%s, %s,%s, %s,%s, %s)",
                                   [miembro['nombre'], miembro['cedula'], miembro['sexo'], miembro['parentesco'], fecha,
                                    ultimoId])
                print('Detalle Creado')
                # Registra la auditoría para la creación de cada miembro de la familia
                # Crear registro de auditoría para la creación de cada miembro
                AuditUser.objects.create(
                    usuario=request.user,
                    tabla="alicuota_miembrofamilia",
                    registroid=ultimoId,
                    accion='A',
                    fecha=timezone.now().date(),
                    hora=timezone.now().time(),
                    estacion=ip_cliente  # Cambia "Estación A" por el valor correcto de la estación
                )
            return Response({'mensaje': 'Familia creada.'}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class BuscarMiembrosFamilia(APIView):
    def get(self, request, id_familia):
        try:
            print(id_familia)
            miembros = MiembroFamilia.objects.filter(familia_id=id_familia)
            print(miembros)
            return Response(miembros.values(), status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({'error': 'Familia no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ModificarFamiliaView(APIView):
    def put(self, request, id_familia):
        try:
            # Obtener la IP del cliente
            ip_cliente = request.META.get('REMOTE_ADDR', '')

            # Cabecera: Actualizar la familia
            familia = FamiliaPropietario.objects.get(id=id_familia)
            descripcion_anterior = familia.descripcion  # Descripción anterior para auditoría
            nueva_descripcion = request.data.get('descripcion')
            familia.descripcion = request.data.get('descripcion')
            familia.save()
            # Registrar auditoría para actualización de la familia
            AuditUser.objects.create(
                usuario=request.user,
                tabla="alicuota_familiapropietario",
                registroid=id_familia,
                accion='M',
                fecha=timezone.now().date(),
                hora=timezone.now().time(),
                estacion=ip_cliente,  # Modificar según el entorno real
            )

            # Detalles: Obtener la lista enviada desde el front
            listaFamilia = request.data.get('listaFamilia')  # Datos enviados desde el front
            miembros = MiembroFamilia.objects.filter(familia_id=id_familia)  # Miembros existentes en la DB

            # Convertir los miembros existentes a un diccionario para fácil acceso usando cédula
            miembros_existentes_dict = {miembro.cedula: miembro for miembro in miembros}

            # Eliminar miembros que no están en la lista del front
            for cedula in list(miembros_existentes_dict.keys()):
                if not any(miembro['cedula'] == cedula for miembro in listaFamilia):
                    miembro = miembros_existentes_dict[cedula]
                    miembro.delete()
                    print(f'Miembro con cédula {cedula} eliminado.')
                    # Registrar auditoría para eliminación de miembro
                    AuditUser.objects.create(
                        usuario=request.user,
                        tabla="alicuota_miembrofamilia",
                        registroid=miembro.id,
                        accion='E',
                        fecha=timezone.now().date(),
                        hora=timezone.now().time(),
                        estacion=ip_cliente,
                    )

            # Agregar o actualizar miembros desde la lista del front
            for miembro_front in listaFamilia:
                cedula = miembro_front['cedula']
                # Si el miembro ya existe, lo actualizamos
                if cedula in miembros_existentes_dict:
                    miembro = miembros_existentes_dict[cedula]
                    miembro.nombre = miembro_front['nombre']
                    miembro.sexo = miembro_front['sexo']
                    miembro.parentesco = miembro_front['parentesco']
                    miembro.fecha_nacimiento = datetime.strptime(miembro_front['fecha_nacimiento'], "%Y-%m-%d")
                    miembro.save()
                    # Registrar auditoría para actualización de miembro
                    AuditUser.objects.create(
                        usuario=request.user,
                        tabla="alicuota_miembrofamilia",
                        registroid=miembro.id,
                        accion='M',
                        fecha=timezone.now().date(),
                        hora=timezone.now().time(),
                        estacion=ip_cliente,
                    )
                    print(f'Miembro con cédula {cedula} actualizado.')
                else:
                    # Si el miembro no existe, lo creamos
                    fecha = datetime.strptime(miembro_front['fecha_nacimiento'], "%Y-%m-%d")
                    nuevo_miembro = MiembroFamilia.objects.create(
                        nombre=miembro_front['nombre'],
                        cedula=cedula,
                        sexo=miembro_front['sexo'],
                        parentesco=miembro_front['parentesco'],
                        fecha_nacimiento=fecha,
                        familia_id=id_familia
                    )
                    print(f'Miembro creado con cédula {cedula}.')
                    # Registrar auditoría para nuevo miembro
                    AuditUser.objects.create(
                        usuario=request.user,
                        tabla="alicuota_miembrofamilia",
                        registroid=nuevo_miembro.id,
                        accion='A',
                        fecha=timezone.now().date(),
                        hora=timezone.now().time(),
                        estacion=ip_cliente,
                    )

            return Response({'mensaje': 'Familia modificada.'}, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({'error': 'Familia no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f'Error en ModificarFamiliaView: {type(e).__name__} - {e}')
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class BuscarInfoViviendaView(APIView):
    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
    av.id AS vivienda_id,
    avi.numero_villa,
    am.codigo_manzana,
    av.descripcion,
    av.valor,
    ar.nombre,
    ar.cedula,
    ar.email
FROM 
    alicuota_vivienda av
LEFT JOIN 
    alicuota_residente ar ON av.residente_id = ar.id
LEFT JOIN 
    alicuota_villa avi ON avi.id = av.villa_id
LEFT JOIN 
    alicuota_manzana am ON avi.manzana_id = am.id
WHERE 
    NOT EXISTS (
        SELECT 1
        FROM alicuota_cabalicuota ac
        WHERE ac.vivienda_id = avi.id
          AND ac.saldo_pendiente > 0
    );
                """)
                # Obtener los resultados de la consulta
                resultados = cursor.fetchall()
                # Crear una lista de diccionarios para retornar los resultados
                data = [
                    {
                        'id': resultado[0],
                        'villa': f'{resultado[2]} - {resultado[1]}',
                        'descripcion': resultado[3],
                        'valor': resultado[4],
                        'nombre': resultado[5],
                        'cedula': resultado[6],
                        'email': resultado[7]
                    } for resultado in resultados
                ]

            print('Consulta realizada con éxito')
            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Guardar la alicuota con todos sus pagos
class GuardarAlicuotaView(APIView):
    def post(self, request):
        try:
            # Obtener la IP del cliente
            ip_cliente = request.META.get('REMOTE_ADDR', '')

            # Obtener la información desde el front
            cabecera = request.data.get('cabecera')
            pagos = request.data.get('pagos')

            # Insertar cabecera
            query = """insert into alicuota_cabalicuota
                        (pago_inicial, saldo_pagar, fecha_creacion, fecha_pago, periodo, monto, saldo_financiar, saldo_pendiente, Interes_id, entrada_tasa_id, vivienda_id, interestotal) 
                        values(%s, %s,%s, %s,%s, %s, %s, %s,%s, %s,%s, %s)"""
            values = [
                cabecera[0]['pago_inicial'], cabecera[0]['saldo_pagar'], cabecera[0]['fecha_creacion'],
                cabecera[0]['fecha_pago'], cabecera[0]['periodo'], cabecera[0]['monto'], cabecera[0]['saldo_financiar'],
                cabecera[0]['saldo_pendiente'], cabecera[0]['Interes_id'], cabecera[0]['entrada_tasa_id'],
                cabecera[0]['vivienda_id'], cabecera[0]['interestotal']
            ]
            with connection.cursor() as cursor:
                cursor.execute(query, values)
                print('Cabecera Creada')

            # Obtener el ID de la cabecera creada
            ultimoId = CabAlicuota.objects.latest('id').id

            # Registrar auditoría para la cabecera creada
            AuditUser.objects.create(
                usuario=request.user,
                tabla="alicuota_cabalicuota",
                registroid=ultimoId,
                accion='A',  # 'A' para indicar creación (Alta)
                fecha=timezone.now().date(),
                hora=timezone.now().time(),
                estacion=ip_cliente
            )

            # Insertar pagos
            queryPagos = """insert into alicuota_detalicuota
                            (secuencia, fecha, fecha_vencimiento, recargo, total, saldo_pagar, estado, cab_alicuota_id) 
                            values (%s, %s,%s, %s,%s, %s, %s, %s)"""
            for pago in pagos:
                valuesPagos = [pago['secuencia'], pago['fecha'], pago['fechaVencimiento'], pago['recargo'],
                               pago['totalPagar'], pago['saldoPendiente'], pago['estado'], ultimoId]
                with connection.cursor() as cursor:
                    cursor.execute(queryPagos, valuesPagos)
                    print('Pago Creado: ', pago['secuencia'])

            # Crear un único registro de auditoría después del bucle
            AuditUser.objects.create(
                usuario=request.user,
                tabla="alicuota_detalicuota",
                registroid=ultimoId,  # Usa el ID de la cabecera o ajusta según sea necesario
                accion='A',
                fecha=timezone.now().date(),
                hora=timezone.now().time(),
                estacion=ip_cliente
            )

            return Response({'AlicuotaCreada': ultimoId}, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# obtener datos de la alicuota
class InfoAlicuota(APIView):
    def get(self, request, id):
        try:
            query = """ select ar.nombre, ar.email,ar.telefono, ar.cedula, ac.monto, ar.id 
                        from alicuota_cabalicuota ac, alicuota_vivienda av, alicuota_residente ar 
                        where ac.vivienda_id = av.id and av.residente_id = ar.id and ac.id = %s """
            values = [id]
            with connection.cursor() as cursor:
                cursor.execute(query, values)
                resultados = cursor.fetchall()
                # Crear una lista de diccionarios para retornar los resultados
                data = [
                    {
                        'nombre': resultado[0],
                        'email': resultado[1],
                        'telefono': resultado[2],
                        'cedula': resultado[3],
                        'monto': resultado[4],
                        'id_residente': resultado[5]
                    } for resultado in resultados
                ]
            queryDetalles = """ select* from alicuota_detalicuota where cab_alicuota_id = %s"""
            with connection.cursor() as cursor:
                cursor.execute(queryDetalles, values)

                columnas = [desc[0] for desc in cursor.description]
                detalles = [dict(zip(columnas, row)) for row in cursor.fetchall()]

                data.append(detalles)

            queryClientes = "select * from alicuota_residente"
            with connection.cursor() as cursor:
                cursor.execute(queryClientes)

                columnas = [desc[0] for desc in cursor.description]
                clientes = [dict(zip(columnas, row)) for row in cursor.fetchall()]

                data.append(clientes)
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# va ha estar arrecha la logica de esta api, ni idea que hacer xddddddd
class GuardarPago(APIView):
    def post(self, request):
        try:
            # Obtener la IP del cliente
            ip_cliente = request.META.get('REMOTE_ADDR', '')

            cliente = request.data.get('cliente')
            cabecera = request.data.get('cabPago')
            pagos = request.data.get('detPago')

            if cliente:
                # Query para guardar al nuevo cliente
                queryCliente = """
                insert into alicuota_residente(nombre, telefono, email, cedula, activo, status, tipo_residente_id, vehiculo_id) 
                values(%s, %s, %s, %s, 0, 0, 1, null)"""
                valuesCliente = [cliente['nombre'], cliente['telefono'], cliente['correo'], cliente['cedula']]

                with connection.cursor() as cursor:
                    cursor.execute(queryCliente, valuesCliente)
                    print('El cliente se ha creado con éxito')

                # Registrar auditoría del cliente creado
                ultimoIdResidente = Residente.objects.latest('id').id
                AuditUser.objects.create(
                    usuario=request.user,
                    tabla="alicuota_residente",
                    registroid=ultimoIdResidente,
                    accion='A',
                    fecha=timezone.now().date(),
                    hora=timezone.now().time(),
                    estacion=ip_cliente
                )

                # Query para guardar la cabecera de la factura
                queryCabecera = """
                insert into alicuota_cabfactura(fecha_creacion, monto, factura, id_cabalicuotra_id, id_residentes_id) 
                values(%s, %s, %s, %s, %s)"""
                valuesCabecera = [cabecera['fecha_creacion'], cabecera['monto'], cabecera['factura'],
                                  cabecera['id_cabalicuotra_id'], ultimoIdResidente]
                with connection.cursor() as cursor:
                    cursor.execute(queryCabecera, valuesCabecera)
                    print('Cabecera del pago se ha creado con éxito')
            else:
                # Query para guardar la cabecera de la factura
                queryCabecera = """
                insert into alicuota_cabfactura(fecha_creacion, monto, factura, id_cabalicuotra_id, id_residentes_id) 
                values(%s, %s, %s, %s, %s)"""
                valuesCabecera = [cabecera['fecha_creacion'], cabecera['monto'], cabecera['factura'],
                                  cabecera['id_cabalicuotra_id'], cabecera['id_residentes_id']]

                with connection.cursor() as cursor:
                    cursor.execute(queryCabecera, valuesCabecera)
                    print('Cabecera del pago se ha creado con éxito')

            # Registrar auditoría para la cabecera de la factura
            ultimoId = CabFactura.objects.latest('id').id
            AuditUser.objects.create(
                usuario=request.user,
                tabla="alicuota_cabfactura",
                registroid=ultimoId,
                accion='A',
                fecha=timezone.now().date(),
                hora=timezone.now().time(),
                estacion=ip_cliente
            )

            # Guardar el detalle de la factura
            queryPagos = """
            insert into alicuota_detfactura(descripcion, valor_pagar, recargo, subtotal, pago, id_cabfactura_id) 
            values (%s, %s, %s, %s, %s, %s)
            """
            for pago in pagos:
                valuesPagos = [pago['descripcion'], pago['valor_pagar'], pago['recargo'], pago['subtotal'],
                               pago['pago'], ultimoId]
                with connection.cursor() as cursor:
                    cursor.execute(queryPagos, valuesPagos)
                    print('Pago Creado: ', pago['descripcion'])
                    # Registrar auditoría para cada pago
            AuditUser.objects.create(
                usuario=request.user,
                tabla="alicuota_detfactura",
                registroid=ultimoId,  # Puedes ajustar si necesitas el ID específico del detalle
                accion='A',
                fecha=timezone.now().date(),
                hora=timezone.now().time(),
                estacion=ip_cliente
            )

            # Actualizar los detalles de las alícuotas
            queryActualizarDetallesA = """
            update alicuota_detalicuota 
            set recargo = %s, saldo_pagar = %s, estado = %s 
            where id = %s
            """
            for pago in pagos:
                valuesActualizarDetallesA = [
                    pago['recargo'], pago['valor_pagar'], pago['estado'], pago['id']
                ]
                with connection.cursor() as cursor:
                    cursor.execute(queryActualizarDetallesA, valuesActualizarDetallesA)
                    print('Detalles de la alícuota actualizados: ', pago['id'])

                # Registrar auditoría para la actualización de alícuotas
                AuditUser.objects.create(
                    usuario=request.user,
                    tabla="alicuota_detalicuota",
                    registroid=pago['id'],
                    accion='M',  # 'M' para modificación
                    fecha=timezone.now().date(),
                    hora=timezone.now().time(),
                    estacion=ip_cliente
                )

            # Actualizar el campo de SaldoPendiente en la cabecera de la alícuota
            with connection.cursor() as cursor:
                cursor.execute('exec ActualizarSaldoPendiente %s', [cabecera['id_cabalicuotra_id']])

            return Response({'facturaCreada': ultimoId}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Generar PDF DEL PAGO
import os
import pdfkit
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.template.loader import render_to_string
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .models import CabFactura, DetFactura


class EnviarPDFPorCorreo(APIView):
    def post(self, request, id):
        try:
            # Obtener los datos de CabFactura y sus detalles
            cabFactura = CabFactura.objects.get(pk=id)
            detalles = DetFactura.objects.filter(id_cabfactura=cabFactura)
            # Obtener la urbanización asociada a la factura
            urbanizacion = cabFactura.id_cabalicuotra.vivienda.villa.manzana.urbanizacion
            # Extraer el nombre y la dirección de la urbanización
            nombre_urbanizacion = urbanizacion.nombre_urbanizacion
            direccion_urbanizacion = urbanizacion.direccion

            for det in detalles:
                det.total_a_pagar = det.valor_pagar + det.recargo

                # Renderizar el HTML con los datos de la factura y detalles
            html = render_to_string('Pago/pago_pdf.html', {
                'cabFactura': cabFactura,
                'detalles': detalles,
                'nombre_urbanizacion': nombre_urbanizacion,
                'direccion_urbanizacion': direccion_urbanizacion})

            # Opciones de configuración para wkhtmltopdf
            options = {
                'page-size': 'A4',
                'orientation': 'Portrait',
                'no-outline': None,
                'enable-local-file-access': None  # Esto puede ser necesario si usas archivos locales en tu HTML
            }
            # Configurar el path de wkhtmltopdf si no está en el PATH
            config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

            # Crear el PDF a partir del HTML renderizado
            pdf_file = pdfkit.from_string(html, False, options=options, configuration=config)

            # Definir la ruta del archivo PDF en la carpeta 'media/pdf/'
            pdf_directory = os.path.join(settings.MEDIA_ROOT, 'pdf')
            if not os.path.exists(pdf_directory):
                os.makedirs(pdf_directory)  # Crear el directorio si no existe

            # Crear el nombre del archivo PDF
            pdf_filename = f"reporte_alicuota_{id}.pdf"
            pdf_filepath = os.path.join(pdf_directory, pdf_filename)

            # Guardar el PDF en el archivo
            with open(pdf_filepath, 'wb') as pdf_file_obj:
                pdf_file_obj.write(pdf_file)

            # Obtener los parámetros del correo desde la solicitud
            to_email = request.data.get("email")
            subject = request.data.get("subject", f"Factura {cabFactura.id} - PDF Adjunto")
            message = request.data.get("message", f"Hola, el PDF de la factura {cabFactura.id} está adjunto.")

            if not to_email:
                return JsonResponse({'error': 'El campo "email" es obligatorio.'}, status=status.HTTP_400_BAD_REQUEST)

            # Crear el correo y adjuntar el archivo PDF
            email = EmailMessage(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [to_email],
            )
            email.attach_file(pdf_filepath)

            # Enviar el correo
            email.send()

            # Retornar una respuesta exitosa
            # Retornar el PDF como respuesta HTTP para abrirlo en una nueva pestaña
            response = HttpResponse(pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="{pdf_filename}"'
            return response

        except Exception as e:
            # En caso de error, devolver una respuesta con el error
            return JsonResponse({'error': f'Ocurrió un error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EnviarPDFPorCorreoalicuota(APIView):
    def post(self, request, id):
        try:
            # Obtener los datos de CabAlicuota y sus detalles
            alicuota = CabAlicuota.objects.get(pk=id)  # Asegúrate de quet esta consulta sea correca
            detalles = DetAlicuota.objects.filter(cab_alicuota=alicuota)
            # Calcular el total acumulado y saldo a pagar acumulado
            total_acumulado = sum(detalle.total for detalle in detalles)
            # Nuevo cálculo: sumar (total + recargo) para el saldo acumulado
            saldo_a_pagar_acumulado = sum(round(detalle.total + detalle.recargo, 2) for detalle in detalles)
            saldo_pendiente = sum(
                (detalle.total + detalle.recargo) for detalle in detalles if detalle.estado.lower() != "pagado"
            )
            print(saldo_a_pagar_acumulado)
            # Agregar un atributo calculado 'total_con_recargo' a cada detalle
            for detalle in detalles:
                detalle.total_con_recargo = round(detalle.total + detalle.recargo, 2)
                # Renderizar el HTML con los datos de la factura y detalles
            html = render_to_string('Alicuota/alicuota_pdf.html', {'alicuota': alicuota,
                                                                   'detalles': detalles,
                                                                   'total_acumulado': total_acumulado,
                                                                   'saldo_acumulado': saldo_a_pagar_acumulado,
                                                                   'saldo_pendiente': saldo_pendiente, })
            # Opciones de configuración para wkhtmltopdf (si es necesario)
            options = {
                'page-size': 'A4',
                'orientation': 'Portrait',
                'no-outline': None,
                'enable-local-file-access': None  # Esto puede ser necesario si usas archivos locales en tu HTML
            }
            # Configurar el path de wkhtmltopdf si no está en el PATH
            config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

            # Crear el PDF a partir del HTML renderizado
            pdf_file = pdfkit.from_string(html, False, options=options, configuration=config)

            # Definir la ruta del archivo PDF en la carpeta 'media/pdf/'
            pdf_directory = os.path.join(settings.MEDIA_ROOT, 'pdf')
            if not os.path.exists(pdf_directory):
                os.makedirs(pdf_directory)  # Crear el directorio si no existe

            # Crear el nombre del archivo PDF
            pdf_filename = f"creacion_alicuota_{id}.pdf"
            pdf_filepath = os.path.join(pdf_directory, pdf_filename)

            # Guardar el PDF en el archivo
            with open(pdf_filepath, 'wb') as pdf_file_obj:
                pdf_file_obj.write(pdf_file)

            # Obtener los parámetros del correo desde la solicitud
            to_email = request.data.get("email")
            subject = request.data.get("subject", f"Alicuota {alicuota.id} - PDF Adjunto")
            message = request.data.get("message", f"Hola, el PDF de la Alicuota {alicuota.id} está adjunto.")

            if not to_email:
                return JsonResponse({'error': 'El campo "email" es obligatorio.'}, status=status.HTTP_400_BAD_REQUEST)

            # Crear el correo y adjuntar el archivo PDF
            email = EmailMessage(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [to_email],
            )
            email.attach_file(pdf_filepath)

            # Enviar el correo
            email.send()

            # Retornar una respuesta exitosa
            # Retornar el PDF como respuesta HTTP para abrirlo en una nueva pestaña
            response = HttpResponse(pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="{pdf_filename}"'
            return response

        except Exception as e:
            # En caso de error, devolver una respuesta con el error
            return JsonResponse({'error': f'Ocurrió un error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

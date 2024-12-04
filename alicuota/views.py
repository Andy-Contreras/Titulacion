from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordResetView
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import View, TemplateView
from django.contrib import messages
from alicuota.mixins import RetornarInicioMixin
from alicuota.models import *
import pdfkit
import locale
from django.db.models import Sum, DateField
from django.db.models.functions import TruncMonth, Cast
import calendar
from datetime import datetime
import requests
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render

# Create your views_system here.

class LoginUserView(RetornarInicioMixin, LoginView):
    extra_context = {'titulo': 'ACA - Inicio de sesión'}

    def post(self, request, *args, **kwargs):
        # Capturamos la respuesta del reCAPTCHA enviada desde el formulario
        recaptcha_response = request.POST.get('g-recaptcha-response')

        # Si el reCAPTCHA no está presente en la solicitud
        if not recaptcha_response:
            return self._render_with_error(request, 'Por favor, completa el reCAPTCHA.')

        # Datos necesarios para enviar a Google reCAPTCHA
        payload = {
            'secret': settings.RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response,
        }
        recaptcha_url = 'https://www.google.com/recaptcha/api/siteverify'

        try:
            # Enviamos la solicitud POST a Google reCAPTCHA
            response = requests.post(recaptcha_url, data=payload)
            result = response.json()

            # Verificamos si la respuesta es exitosa
            if not result.get('success'):
                return self._render_with_error(request, 'Por favor, completa el reCAPTCHA correctamente.')

        except requests.RequestException as e:
            return self._render_with_error(request, f'Error al verificar el reCAPTCHA: {str(e)}, intenta nuevamente.')

        # Eliminamos el error del reCAPTCHA de la sesión, si existe
        if 'recaptcha_error' in request.session:
            del request.session['recaptcha_error']

        # Continuamos con el inicio de sesión estándar
        return super().post(request, *args, **kwargs)

    def _render_with_error(self, request, error_message):
        """
        Renderiza la página de inicio de sesión con un mensaje de error.
        """
        # Guardamos el error en la sesión para poder mostrarlo en la plantilla
        request.session['recaptcha_error'] = True
        messages.error(request, error_message)

        # Pasa el formulario y otros contextos, como 'titulo', si lo necesitas
        context = {'form': self.get_form(), 'titulo': self.extra_context['titulo']}
        return render(request, self.template_name, context)


class InicioTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'inicio.html'

    def abbreviate_number(self, number):
        """Abreviar números con decimales, mostrar M solo para valores grandes (millones)."""
        if number >= 1_000_000:  # Si el número es 1 millón o más
            if number % 1_000_000 == 0:
                return f"{int(number / 1_000_000)}M"
            else:
                return f"{number:,.2f}"  # Mostrar con comas y decimales
        else:
            return f"{number:.2f}"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Panel Administrativo'
        context['residentes'] = Residente.objects.filter(status=True).count()
        context['viviendas'] = Vivienda.objects.count()
        # Configurar el formato local (español)
        locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')

        # Total de montos de CabFactura
        total_monto = CabFactura.objects.aggregate(total=Sum('monto'))['total']
        # Formatear el monto en formato español
        context['finanzas'] = self.abbreviate_number(total_monto) if total_monto else '0.00'  # Aquí se usa self


        # Obtener rango de fechas desde la solicitud
        fecha_inicio = self.request.GET.get('start_date')
        fecha_fin = self.request.GET.get('end_date')

        # Si no se especifica, usar valores predeterminados
        if not fecha_inicio:
            fecha_inicio = datetime(datetime.now().year, 1, 1).date()  # Inicio del año actual
        else:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()

        if not fecha_fin:
            fecha_fin = datetime(datetime.now().year, 12, 31).date()  # Fin del año actual
        else:
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()

        context['fecha_inicio'] = fecha_inicio
        context['fecha_fin'] = fecha_fin

        # Inicializar diccionario de meses
        meses_del_ano = {month: 0 for month in range(1, 13)}

        # Filtrar los pagos dentro del rango de fechas y agruparlos por mes
        pagos_por_mes = (
            DetFactura.objects.annotate(
                fecha=Cast('descripcion', DateField())  # Convertir 'descripcion' a DateField
            )
            .filter(fecha__range=[fecha_inicio, fecha_fin])  # Filtrar por el rango de fechas
            .annotate(mes=TruncMonth('fecha'))  # Agrupar por mes
            .values('mes')
            .annotate(total_subtotal=Sum('subtotal'))  # Sumar subtotales
            .order_by('mes')
        )

        # Actualizar los valores de los meses existentes
        for pago in pagos_por_mes:
            mes = pago['mes'].month
            meses_del_ano[mes] = float(pago['total_subtotal'])

        # Convertir datos para el gráfico
        context['grafico_meses'] = [calendar.month_name[mes] for mes in meses_del_ano]
        context['grafico_totales'] = list(meses_del_ano.values())

        return context


class CustomPasswordResetView(PasswordResetView):
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    html_email_template_name = 'registration/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')
    extra_context = {'titulo': 'ACA - Recuperar Contraseña'}

    def post(self, request, *args, **kwargs):
        # Obtener el correo ingresado desde el formulario
        email = request.POST.get('email')

        # Verificar si el correo está registrado
        if not User.objects.filter(email=email).exists():
            # Si el correo no existe, mostrar un mensaje de error
            messages.error(request, "El correo ingresado no está registrado.")
            return render(request, self.template_name, {
                'form': self.get_form(),
                'titulo': 'ACA - Recuperar Contraseña'
            })

        # Si el correo es válido, continuar con el proceso normal de restablecimiento
        messages.success(request, "Si el correo es correcto, recibirás un enlace para restablecer tu contraseña.")
        return super().post(request, *args, **kwargs)



class PDFReporteAlicuotaView(View):
    def get(self, request, pk):
        # Obtener los datos de CabAlicuota y sus detalles
        alicuota = CabAlicuota.objects.get(pk=pk)  # Asegúrate de quet esta consulta sea correca
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
        # Renderizar el HTML con los datos de alícuota y detalles
        html = render_to_string('Alicuota/alicuota_pdf.html', {'alicuota': alicuota,
                                                               'detalles': detalles, 'total_acumulado': total_acumulado,
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

        # Configurar la respuesta HTTP para mostrar el PDF en el navegador
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="reporte_alicuota_{pk}.pdf"'

        return response

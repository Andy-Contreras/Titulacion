from email.message import Message
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.translation.template import context_re
from django.views.generic import ListView, CreateView, DeleteView, UpdateView, TemplateView, DetailView
from alicuota.models import *
from django.shortcuts import get_object_or_404
from django.db.models import Q, Value
from django.db.models.functions import Concat

class Pago_AlicuotaListView(LoginRequiredMixin, ListView):
    template_name = 'Pago/listado_alicuota.html'
    model = CabAlicuota
    context_object_name = 'alicuota'

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '').strip()

        if search_query:
            # Crear un campo virtual combinando `manzana.codigo_manzana` y `numero_villa`
            queryset = queryset.annotate(
                codigo_completo=Concat(
                    'vivienda__villa__manzana__codigo_manzana',
                    Value('-'),
                    'vivienda__villa__numero_villa'
                )
            ).filter(
                Q(codigo_completo__icontains=search_query) |  # Filtrar por código completo
                Q(vivienda__residente__cedula__icontains=search_query)  # Filtrar por cédula
            )
        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Listado de Pago'

        # Obtener los detalles de los pagos
        detalles = DetAlicuota.objects.all()


        # Pasar los detalles y el total acumulado al contexto
        context['detalles'] = detalles
        context['search_query'] = self.request.GET.get('search', '')
        context['listar_url'] = '/alicuota_lista'
        return context


class PagoListView(LoginRequiredMixin, TemplateView):
    template_name = 'Pago/crear_pago.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Recibo de Pago'
        context['cancel_url'] = reverse_lazy('alicuota_lista')

        # Supongamos que tienes una forma de obtener la instancia de la factura o el residente
        # Aquí obtienes el primer 'CabFactura' como ejemplo. Cambia esto según lo necesites.
        cab_factura = CabFactura.objects.first()  # O usa un filtro más específico, si es necesario

        # Acceder a la urbanización a través de las relaciones de los modelos
        if cab_factura:
            vivienda = cab_factura.id_cabalicuotra.vivienda  # Accedemos a la vivienda
            villa = vivienda.villa  # Accedemos a la villa
            manzana = villa.manzana  # Accedemos a la manzana
            urbanizacion = manzana.urbanizacion  # Accedemos a la urbanización

            # Añadir el nombre y la dirección de la urbanización al contexto
            context['nombre_urbanizacion'] = urbanizacion.nombre_urbanizacion
            context['direccion_urbanizacion'] = urbanizacion.direccion

        return context

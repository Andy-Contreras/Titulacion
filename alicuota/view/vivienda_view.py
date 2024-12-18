from email.message import Message

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation.template import context_re
from django.views.generic import ListView,CreateView,DeleteView, UpdateView
from requests.utils import super_len
from django.contrib import messages
from alicuota.forms import ViviendaForm
from alicuota.models import *
from django.urls import reverse_lazy

class ViviendaListView(LoginRequiredMixin, ListView):
    template_name = 'Vivienda/lista_vivienda.html'
    model =  Vivienda

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("query")
        status = self.request.GET.get("status")
        if query:
            queryset = queryset.filter(residente__nombre__icontains=query)
        if status == 'disponible':
            queryset = queryset.filter(estado=False)
        elif status == 'ocupado':
            queryset = queryset.filter(estado=True)
        return queryset



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Listado de Vivienda'
        context['buscar'] = 'Buscar por nombre del residente'
        context['btn_crear'] = 'Crear Vivienda'
        context['url_crear'] = '/vivienda_crear'
        context['btn_actualizar'] = '/vivienda_actualizar'
        return context


class ViviendaCreateView(LoginRequiredMixin, CreateView):
    template_name = 'Vivienda/crear_vivienda.html'
    model = Vivienda
    form_class = ViviendaForm
    success_url = reverse_lazy('vivienda_lista')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'NUEVO REGISTRO'
        context['action_save'] = '/vivienda_crear/'
        context['listar_url'] = '/vivienda_lista/'
        context['cancel_url'] = reverse_lazy('vivienda_lista')
        return context

    def form_valid(self, form):
        vivienda = form.save(commit=False)

        # Verificamos si hay un residente asignado
        if vivienda.residente:
            vivienda.estado = True  # Si tiene residente, la vivienda está ocupada
        else:
            vivienda.estado = False  # Si no tiene residente, la vivienda está disponible

        # Guardamos la vivienda con el estado correcto
        response = super().form_valid(form)

        # Audit logging (asumido que tienes la función save_audit)
        save_audit(self.request, vivienda, action='A')

        # Mensaje de éxito
        messages.success(self.request, f"Éxito al Crear la Vivienda {vivienda.villa}.")
        return response


class ViviendaUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'Vivienda/crear_vivienda.html'
    model = Vivienda
    form_class = ViviendaForm
    success_url = reverse_lazy('vivienda_lista')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'ACTUALZIAR REGISTRO'
        context['action_save'] = self.request.path
        context['cancel_url'] = reverse_lazy('vivienda_lista')
        return context

    def form_valid(self, form):
        vivienda = form.save(commit=False)

        # Verificamos si el residente ha sido asignado o removido
        if vivienda.residente:
            vivienda.estado = True  # Si tiene residente, la vivienda está ocupada
        else:
            vivienda.estado = False  # Si no tiene residente, la vivienda está disponible

        # Guardamos los cambios con el estado correcto
        response = super().form_valid(form)

        # Audit logging (asumido que tienes la función save_audit)
        save_audit(self.request, vivienda, action='M')

        # Mensaje de éxito
        messages.success(self.request, f"Éxito al Modificar la Vivienda {vivienda.villa}.")
        return response



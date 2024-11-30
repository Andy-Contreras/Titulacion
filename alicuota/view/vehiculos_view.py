from email.message import Message
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.utils.translation.template import context_re
from django.views.generic import ListView,CreateView,DeleteView, UpdateView
from requests.utils import super_len
from django.contrib import messages
from alicuota.forms import VehiculoForm
from alicuota.models import *
from django.urls import reverse_lazy


class VehiculoListView(LoginRequiredMixin, ListView):
    template_name = 'Vehiculo/listado_vehiculo.html'
    model = Vehiculo
    queryset = Vehiculo.objects.filter(activo=True)
    def get_queryset(self):
        query = self.request.GET.get("query")
        if query:
            return self.model.objects.filter(placa__icontains=query)
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Listado de Vehículos'
        context['buscar'] = 'Buscar por placa'
        context['btn_crear'] = 'Crear Vehiculos'
        context['url_crear'] = '/vehiculo_crear'
        context['btn_eliminar'] = '/vehiculo_eliminar'
        context['btn_actualizar'] = '/vehiculo_actualizar'
        context['query'] = self.request.GET.get("query")
        context['listar_url'] = '/vehiculos_lista/'
        return context


class VehiculoCreateView(LoginRequiredMixin, CreateView):
    template_name = 'Vehiculo/crear_vehiculo.html'
    model = Vehiculo
    form_class = VehiculoForm
    success_url = reverse_lazy('vehiculo_lista')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'NUEVO REGISTRO'
        context['action_save'] = '/vehiculo_crear/'
        context['listar_url'] = '/vehiculo_lista/'
        context['cancel_url'] = reverse_lazy('vehiculo_lista')
        return context
    def form_valid(self, form):
        response = super().form_valid(form)
        patient = self.object
        save_audit(self.request, patient, action='A')
        messages.success(self.request, f"Éxito al Modificar el Residente {patient.placa}.")
        print("mande mensaje")
        return response

class VehiculoDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'vehiculo/eliminar_vehiculo.html'
    model = Vehiculo
    success_url = reverse_lazy('vehiculo_lista')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'ELIMINAR VEHICULO'
        context['action_save'] = self.request.path
        context['cancel_url'] = reverse_lazy('vehiculo_lista')
        return context
    def form_valid(self, form):
        # Guardar auditoría antes de eliminar
        Vehiculo = self.get_object()
        save_audit(self.request, Vehiculo, action='E')
        # Acción de eliminación
        messages.success(self.request, f"Vehiculo {Vehiculo.placa} eliminado correctamente.")
        return super().form_valid(form)
    def delete(self, request, *args, **kwargs):
        # Aquí se maneja la eliminación en sí, llamando a la función base
        response = super().delete(request, *args, **kwargs)
        return response
    def post(self, request, pk, *args, **kwargs):
        object = Vehiculo.objects.get(id=pk)
        object.activo = False
        object.save()
        return redirect('vehiculo_lista')


class VehiculoUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'Vehiculo/crear_vehiculo.html'
    model = Vehiculo
    form_class = VehiculoForm
    success_url = reverse_lazy('vehiculo_lista')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'ACTUALIZAR VEHÍCULO'
        context['action_save'] = self.request.path
        context['cancel_url'] = reverse_lazy('vehiculo_lista')
        return context
    def form_valid(self, form):
        response = super().form_valid(form)
        patient = self.object
        save_audit(self.request, patient, action='M')
        messages.success(self.request, f"Éxito al Modificar el Vehiculo {patient.placa}.")
        print("mande mensaje")
        return response
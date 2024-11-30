from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation.template import context_re
from django.views.generic import ListView, CreateView, UpdateView, TemplateView
from alicuota.forms import FamiliaPropietarioForm, MiembroFamiliaForm
from alicuota.models import *
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q



class FamiliaListView(LoginRequiredMixin, ListView):
    template_name = 'Familia_Residente/lista_familia.html'
    model = FamiliaPropietario

    def get_queryset(self):
        query = self.request.GET.get("query")
        # Filtrar por residentes activos
        queryset = self.model.objects.filter(residente__activo=True)
        if query:
            # Filtrar por el nombre del residente
            queryset = queryset.filter(
                Q(residente__nombre__icontains=query) | Q(descripcion__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Listado de Familia'
        context['btn_crear'] = 'Crear Familia'
        context['buscar'] = 'Buscar Familia'
        context['url_crear'] = '/familia_crear'
        context['btn_actualizar'] = '/familia_actualizar'
        context['listar_url'] = '/familia_lista/'
        return context

class FamiliaCreateView(LoginRequiredMixin, TemplateView):
    template_name = 'Familia_Residente/crear_familia.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Crear Familia'
        context['residentes'] = Residente.objects.all()
        context['action_save'] = '/familia_crear/'
        context['cancel_url'] = reverse_lazy('familia_lista')
        context['guarda_url'] = reverse_lazy('familia_lista')
        return context

class FamiliaUpdateView(LoginRequiredMixin, TemplateView):
    template_name = 'Familia_Residente/editar_familia.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener el valor de pk desde kwargs
        pk = self.kwargs.get('pk')
        propietario = FamiliaPropietario.objects.get(id=pk)
        print(propietario)
        context['titulo'] = 'Editar Familia'
        # Vamos a traer la informacion del propietraio a modificar.
        context['propietario'] = propietario
        context['action_save'] = '/familia_crear/'
        context['cancel_url'] = reverse_lazy('familia_lista')
        context['guarda_url'] = reverse_lazy('familia_lista')

        return context

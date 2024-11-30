# from email.message import Message
#
# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.utils.translation.template import context_re
# from django.views.generic import ListView,CreateView,DeleteView, UpdateView
# from requests.utils import super_len
#
# from alicuota.forms import ClienteForm
# from alicuota.models import *
# from django.urls import reverse_lazy
#
# class ClienteListView(LoginRequiredMixin, ListView):
#     template_name = 'Cliente/lista_cliente.html'
#     model = Cliente
#
#     def get_queryset(self):
#         query = self.request.GET.get("query")
#         if query:
#             return self.model.objects.filter(nombre__icontains=query)
#         return super().get_queryset()
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['titulo'] = 'Listado de Clientes'
#         context['buscar'] = 'Buscar cliente'
#         context['btn_crear'] = 'Crear Cliente'
#         context['url_crear'] = '/cliente_crear'
#         context['btn_eliminar'] = '/cliente_eliminar'
#         context['btn_actualizar'] = '/cliente_actualizar'
#         return context
#
# class ClienteCreateView(LoginRequiredMixin, CreateView):
#     template_name = 'Cliente/crear_cliente.html'
#     model = Cliente
#     form_class = ClienteForm
#     success_url = reverse_lazy('cliente_lista')
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['titulo'] = 'NUEVO REGISTRO'
#         context['action_save'] = '/cliente_crear/'
#         context['listar_url'] = '/cliente_lista/'
#         context['cancel_url'] = reverse_lazy('cliente_lista')
#         return context
#
#
# class ClienteDeleteView(LoginRequiredMixin, DeleteView):
#     template_name = 'Cliente/eliminar_cliente.html'
#     model = Cliente
#     success_url = reverse_lazy('cliente_lista')
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['titulo'] = 'ELIMINAR CLIENTE'
#         context['action_save'] = self.request.path
#         context['cancel_url'] = reverse_lazy('cliente_lista')
#         return context
#
# class ClienteUpdateView(LoginRequiredMixin, UpdateView):
#     template_name = 'Cliente/crear_cliente.html'
#     model = Cliente
#     form_class = ClienteForm
#     success_url = reverse_lazy('cliente_lista')
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['titulo'] = 'ACTUALZIAR CLIENTE'
#         context['action_save'] = self.request.path
#         context['cancel_url'] = reverse_lazy('cliente_lista')
#         return context
#
#
#
#

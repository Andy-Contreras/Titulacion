from email.message import Message

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation.template import context_re
from django.views.generic import ListView,CreateView,DeleteView, UpdateView, TemplateView
from requests.utils import super_len
from alicuota.models import *
from django.urls import reverse_lazy

class AlicuotaCreateView(LoginRequiredMixin, TemplateView):
    template_name = 'Alicuota/crear_alicuota.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasaEntrada'] = TasaEntrada.objects.all()
        print(context['tasaEntrada'])
        context['tasaInteres'] = TasaInterez.objects.all()
        print(context['tasaInteres'])
        context['titulo'] = 'Crear Alicuota'
        context['buscar'] = 'Buscar Alicuota'
        context['btn_crear'] = 'Crear Alicuota'
        context['url_crear'] = '/alicuota_crear'
        context['btn_actualizar'] = '/alicuota_actualizar'
        return context

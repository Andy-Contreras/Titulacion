from django.urls import path, include
from rest_framework import routers

from alicuota.apis import CrearFamiliaView, ValidacionesPersonaFamiliaView, BuscarMiembrosFamilia, ModificarFamiliaView, \
    BuscarInfoViviendaView, GuardarAlicuotaView, InfoAlicuota, GuardarPago, EnviarPDFPorCorreo,EnviarPDFPorCorreoalicuota

urlpatterns = [
    path('crear_familia/', CrearFamiliaView.as_view(), name='crear_familia'),
    path('validar_persona_familia/', ValidacionesPersonaFamiliaView.as_view(), name='validar_persona_familia'),
    path('buscar_miembros_familia/<int:id_familia>/', BuscarMiembrosFamilia.as_view(), name='buscar_miembros_familia'),
    path('modificar_familia/<int:id_familia>/', ModificarFamiliaView.as_view(), name='modificar_familia'),
    path('buscar_vivienda/', BuscarInfoViviendaView.as_view(), name='buscar_vivienda'),
    path('crear_alicuota/', GuardarAlicuotaView.as_view(), name='crear_alicuota'),
    path('generar_pdfAlicuota/<int:id>', EnviarPDFPorCorreoalicuota.as_view(), name='generar_pdfAlicuota'),
    path('info_alicuota/<int:id>', InfoAlicuota.as_view(), name='info_alicuota'),
    path('guardar_pago/', GuardarPago.as_view(), name='guardar_pago'),
    path('generar_pdfPago/<int:id>', EnviarPDFPorCorreo.as_view(), name='generar_pdfPago'),
]

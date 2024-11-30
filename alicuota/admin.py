# Register your models here.
from django.contrib import admin
from alicuota.models import  Urbanizacion, Manzana,Villa, TipoVivienda, Marca, Modelo, TasaEntrada, TasaInterez, TipoResidente
from django.contrib.auth.models import Group, User


# Configuración Urbanización
class UrbanizacionAdmin(admin.ModelAdmin):
    list_display = ('nombre_urbanizacion', 'direccion')
    search_fields = ('nombre_urbanizacion',)
admin.site.register(Urbanizacion, UrbanizacionAdmin)

# Configuración Manzana
class ManzanaAdmin(admin.ModelAdmin):
    list_display = ('codigo_manzana', 'urbanizacion')
    list_filter = ('urbanizacion',)
    search_fields = ('codigo_manzana',)
admin.site.register(Manzana, ManzanaAdmin)

# Configuración Villa
class VillaAdmin(admin.ModelAdmin):
    list_display = ('numero_villa', 'manzana')
    list_filter = ('manzana',)
    search_fields = ('numero_villa',)
admin.site.register(Villa, VillaAdmin)

#TipoVivienda
class TipoViviendaAdmin(admin.ModelAdmin):
    list_display = ('descripcion',)
    search_fields = ('descripcion',)
admin.site.register(TipoVivienda, TipoViviendaAdmin)

# Configuración del modelo Marca en el admin
class MarcaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_marca',)  # Cambié 'id_marca' a 'id'
    ordering = ('nombre_marca',)
    search_fields = ('nombre_marca',)

admin.site.register(Marca, MarcaAdmin)

# Configuración del modelo Modelo en el admin
class ModeloAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_modelo', 'marca',)
    ordering = ('nombre_modelo',)
    search_fields = ('nombre_modelo',)

admin.site.register(Modelo, ModeloAdmin)

# Configuración de Tasa Interes
class TasaInterezAdmin(admin.ModelAdmin):
    list_display = ('porcentaje',)
    search_fields = ('porcentaje',)
admin.site.register(TasaInterez,TasaInterezAdmin)

# Configuración de Tasa Entrada
class TasaEntradaAdmin(admin.ModelAdmin):
    list_display = ('porcentaje',)
    search_fields = ('porcentaje',)
admin.site.register(TasaEntrada,TasaEntradaAdmin)

# Configuracion Tipo Residente
class TipoResidenteAdmin(admin.ModelAdmin):
    list_display = ('descripcion',)
admin.site.register(TipoResidente, TipoResidenteAdmin)

#  Desregistrar los modelos de User y Group

admin.site.unregister(Group)

admin.site.site_header = "Configuración"
admin.site.site_title = "Configuración"
admin.site.index_title = "Configuración"



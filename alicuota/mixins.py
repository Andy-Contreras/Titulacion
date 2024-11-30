from django.shortcuts import redirect


class RetornarInicioMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('inicio')

        return super().dispatch(request, *args, **kwargs)
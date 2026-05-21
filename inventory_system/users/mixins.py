from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy


class RoleRequiredMixin(LoginRequiredMixin):
    allowed_roles = []
    login_url = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        profile = getattr(request.user, 'profile', None)
        if not profile or profile.role not in self.allowed_roles:
            messages.error(request, 'No tienes permisos para acceder a esta página.')
            return redirect(reverse_lazy('dashboard'))

        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['admin']


class OperatorRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['operator']

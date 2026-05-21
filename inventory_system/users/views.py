from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.forms import UserCreationForm

from .mixins import AdminRequiredMixin, OperatorRequiredMixin, RoleRequiredMixin


class AuthLoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        messages.success(self.request, 'Bienvenido de nuevo.')
        return super().form_valid(form)


class AuthLogoutView(LogoutView):
    next_page = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'Has cerrado sesión correctamente.')
        return super().dispatch(request, *args, **kwargs)


class DashboardView(RoleRequiredMixin, TemplateView):
    template_name = 'users/dashboard.html'
    allowed_roles = ['admin', 'operator']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_role'] = getattr(self.request.user.profile, 'role', 'operator')
        context['features'] = [
            'Login y control de roles (Admin / Operador)',
            'CRUD de productos, categorías y proveedores',
            'Registro de compras y ventas',
            'Control automático del stock',
            'Alertas por bajo inventario',
            'Panel de reportes interactivo',
            'Gráficos: productos más vendidos y stock por categoría',
            'Exportación de reportes a CSV (Excel)',
            'Historial completo de movimientos',
            'Generación de facturas en PDF',
        ]
        return context


class AdminAreaView(AdminRequiredMixin, TemplateView):
    template_name = 'users/admin_area.html'


class OperatorAreaView(OperatorRequiredMixin, TemplateView):
    template_name = 'users/operator_area.html'


class RegisterView(CreateView):
    template_name = 'users/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.success(self.request, 'Cuenta creada exitosamente. Ahora puedes iniciar sesión.')
        return super().form_valid(form)

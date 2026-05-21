from django.urls import path

from .views import (
    AdminAreaView,
    AuthLoginView,
    AuthLogoutView,
    DashboardView,
    OperatorAreaView,
    RegisterView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', AuthLoginView.as_view(), name='login'),
    path('logout/', AuthLogoutView.as_view(), name='logout'),
    path('', DashboardView.as_view(), name='dashboard'),
    path('admin-area/', AdminAreaView.as_view(), name='admin_area'),
    path('operator-area/', OperatorAreaView.as_view(), name='operator_area'),
]

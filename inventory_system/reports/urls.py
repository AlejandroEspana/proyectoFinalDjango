from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('dashboard/', views.DashboardReportView.as_view(), name='dashboard'),
    path('export/csv/', views.ExportTransactionsCSVView.as_view(), name='export_csv'),
]

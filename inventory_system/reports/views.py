import csv
from django.http import HttpResponse
from django.db.models import Sum, Q
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from users.mixins import RoleRequiredMixin
from transactions.models import Transaction
from inventory.models import Product, Category

class DashboardReportView(RoleRequiredMixin, TemplateView):
    template_name = 'reports/dashboard.html'
    allowed_roles = ['admin', 'operator']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 1. KPI Cards
        # Total de Ventas (Valor total facturado)
        total_sales_value = Transaction.objects.filter(
            transaction_type=Transaction.TransactionType.SELL
        ).aggregate(total=Sum('total_price'))['total'] or 0.00
        context['total_sales_value'] = total_sales_value

        # Total de Compras (Valor total gastado)
        total_buys_value = Transaction.objects.filter(
            transaction_type=Transaction.TransactionType.BUY
        ).aggregate(total=Sum('total_price'))['total'] or 0.00
        context['total_buys_value'] = total_buys_value

        # Productos en Inventario (cantidad física de items)
        total_products_count = Product.objects.count()
        context['total_products_count'] = total_products_count

        # Productos con stock bajo
        # Un producto tiene stock bajo si product.stock <= product.low_stock_threshold
        low_stock_count = 0
        products = Product.objects.all()
        for p in products:
            if p.is_low_stock:
                low_stock_count += 1
        context['low_stock_count'] = low_stock_count

        # 2. Datos para Gráfico: Productos Más Vendidos
        top_selling_queryset = (
            Transaction.objects.filter(transaction_type=Transaction.TransactionType.SELL)
            .values('product__name')
            .annotate(total_qty=Sum('quantity'))
            .order_by('-total_qty')[:5]
        )
        top_product_labels = [item['product__name'] for item in top_selling_queryset]
        top_product_data = [item['total_qty'] for item in top_selling_queryset]
        context['top_product_labels'] = top_product_labels
        context['top_product_data'] = top_product_data

        # 3. Datos para Gráfico: Stock por Categoría
        category_stock_queryset = (
            Product.objects.values('category__name')
            .annotate(total_stock=Sum('stock'))
            .order_by('category__name')
        )
        category_labels = []
        category_data = []
        for item in category_stock_queryset:
            label = item['category__name'] if item['category__name'] else "Sin Categoría"
            category_labels.append(label)
            category_data.append(item['total_stock'] or 0)
        context['category_labels'] = category_labels
        context['category_data'] = category_data

        return context

class ExportTransactionsCSVView(RoleRequiredMixin, View):
    allowed_roles = ['admin', 'operator']

    def get(self, request, *args, **kwargs):
        # Configurar la respuesta http para descarga de CSV
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="reporte_transacciones.csv"'

        # Escribir BOM de UTF-8 para que Excel reconozca caracteres en español
        response.write('\ufeff')

        writer = csv.writer(response, delimiter=';')
        
        # Cabeceras del CSV
        writer.writerow([
            'Fecha y Hora', 
            'Tipo de Transacción', 
            'Producto', 
            'Categoría', 
            'Cantidad', 
            'Precio Unitario', 
            'Total', 
            'Usuario'
        ])

        # Obtener todas las transacciones ordenadas cronológicamente por fecha descendiente
        transactions = Transaction.objects.select_related('product', 'product__category', 'user').order_by('-date')

        # Aplicar filtros si existen en la petición GET
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        transaction_type = request.GET.get('transaction_type')

        if start_date:
            transactions = transactions.filter(date__date__gte=start_date)
        if end_date:
            transactions = transactions.filter(date__date__lte=end_date)
        if transaction_type:
            transactions = transactions.filter(transaction_type=transaction_type)

        for tx in transactions:
            category_name = tx.product.category.name if tx.product.category else 'Sin categoría'
            writer.writerow([
                tx.date.strftime('%Y-%m-%d %H:%M:%S'),
                tx.get_transaction_type_display(),
                tx.product.name,
                category_name,
                tx.quantity,
                f"{tx.unit_price:.2f}",
                f"{tx.total_price:.2f}",
                tx.user.username
            ])

        return response

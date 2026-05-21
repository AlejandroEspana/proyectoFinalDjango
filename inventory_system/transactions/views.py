from io import BytesIO
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.exceptions import ValidationError

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from users.mixins import RoleRequiredMixin
from .models import Transaction
from .forms import TransactionForm
from .services import process_transaction
from inventory.models import Product

class TransactionListView(RoleRequiredMixin, ListView):
    model = Transaction
    template_name = 'transactions/transaction_list.html'
    context_object_name = 'transactions'
    allowed_roles = ['admin', 'operator']
    ordering = ['-date']

class TransactionCreateView(RoleRequiredMixin, CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'transactions/transaction_form.html'
    success_url = reverse_lazy('transactions:transaction_list')
    allowed_roles = ['admin', 'operator']

    def form_valid(self, form):
        product = form.cleaned_data['product']
        transaction_type = form.cleaned_data['transaction_type']
        quantity = form.cleaned_data['quantity']
        unit_price = form.cleaned_data['unit_price']
        user = self.request.user

        try:
            # Procesar la transacción a través de la capa de servicios
            process_transaction(
                product=product,
                transaction_type=transaction_type,
                quantity=quantity,
                unit_price=unit_price,
                user=user
            )
            messages.success(self.request, "Transacción registrada y stock actualizado correctamente.")
            return redirect(self.success_url)
        except ValidationError as e:
            # Cargar el mensaje de error en el formulario
            form.add_error(None, e.message)
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pasar los precios actuales de los productos para la interacción en el frontend
        products = Product.objects.all()
        product_prices = {p.id: float(p.price) for p in products}
        context['product_prices'] = product_prices
        return context

class GenerateInvoicePDFView(RoleRequiredMixin, View):
    allowed_roles = ['admin', 'operator']

    def get(self, request, pk, *args, **kwargs):
        tx = get_object_or_404(Transaction, pk=pk)
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="factura_{tx.id}.pdf"'
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=letter,
            rightMargin=40, 
            leftMargin=40,
            topMargin=40, 
            bottomMargin=40
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # Estilos Personalizados
        title_style = ParagraphStyle(
            'InvoiceTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=22,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=15,
            alignment=1  # Centrado
        )
        
        normal_style = ParagraphStyle(
            'InvoiceNormal',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            textColor=colors.HexColor('#374151'),
            spaceAfter=6
        )
        
        bold_style = ParagraphStyle(
            'InvoiceBold',
            parent=normal_style,
            fontName='Helvetica-Bold'
        )

        header_style = ParagraphStyle(
            'InvoiceHeaderStyle',
            parent=normal_style,
            fontName='Helvetica-Bold',
            textColor=colors.whitesmoke
        )

        # Encabezado
        story.append(Paragraph("COMPROBANTE DE TRANSACCION", title_style))
        story.append(Spacer(1, 10))
        
        # Tabla de Metadata
        data_info = [
            [
                Paragraph("<b>No. Transacción:</b>", normal_style), 
                Paragraph(str(tx.id), normal_style),
                Paragraph("<b>Fecha:</b>", normal_style), 
                Paragraph(tx.date.strftime("%d/%m/%Y %H:%M"), normal_style)
            ],
            [
                Paragraph("<b>Tipo de Operación:</b>", normal_style), 
                Paragraph(tx.get_transaction_type_display(), normal_style),
                Paragraph("<b>Registrado por:</b>", normal_style), 
                Paragraph(tx.user.username, normal_style)
            ]
        ]
        t_info = Table(data_info, colWidths=[120, 140, 100, 160])
        t_info.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f9fafb')),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#f3f4f6')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(t_info)
        story.append(Spacer(1, 20))
        
        # Detalles de los items
        story.append(Paragraph("<b>Detalles del Producto</b>", styles['Heading3']))
        story.append(Spacer(1, 8))
        
        headers = ["Producto", "Categoría", "Cantidad", "Precio Unitario", "Total"]
        data_items = [
            [Paragraph(h, header_style) for h in headers],
            [
                Paragraph(tx.product.name, normal_style),
                Paragraph(tx.product.category.name if tx.product.category else "Sin categoría", normal_style),
                Paragraph(str(tx.quantity), normal_style),
                Paragraph(f"${tx.unit_price:.2f}", normal_style),
                Paragraph(f"${tx.total_price:.2f}", normal_style)
            ]
        ]
        
        t_items = Table(data_items, colWidths=[180, 110, 60, 90, 80])
        t_items.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(t_items)
        story.append(Spacer(1, 25))
        
        # Fila del total
        data_summary = [
            ["", "", Paragraph("<b>VALOR TOTAL:</b>", bold_style), Paragraph(f"<b>${tx.total_price:.2f}</b>", bold_style)]
        ]
        t_summary = Table(data_summary, colWidths=[180, 110, 150, 80])
        t_summary.setStyle(TableStyle([
            ('PADDING', (0, 0), (-1, -1), 8),
            ('LINEABOVE', (2, 0), (3, 0), 1.5, colors.HexColor('#1f2937')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(t_summary)
        
        # Nota al pie
        story.append(Spacer(1, 50))
        story.append(Paragraph("<font color='#9ca3af'>* Comprobante generado automáticamente por el sistema de inventario.</font>", normal_style))
        
        doc.build(story)
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response

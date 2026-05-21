from django.db import models
from django.contrib.auth.models import User
from inventory.models import Product

class Transaction(models.Model):
    class TransactionType(models.TextChoices):
        BUY = 'buy', 'Compra (Entrada)'
        SELL = 'sell', 'Venta (Salida)'

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(
        max_length=10, 
        choices=TransactionType.choices,
        verbose_name="Tipo de transacción"
    )
    quantity = models.PositiveIntegerField(verbose_name="Cantidad")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio unitario")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False, verbose_name="Precio total")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y hora")
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='transactions', verbose_name="Usuario")

    def save(self, *args, **kwargs):
        # Calculate total_price before saving
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.product.name} ({self.quantity})"

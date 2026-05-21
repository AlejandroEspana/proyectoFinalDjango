from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Transaction
from inventory.models import Product

def process_transaction(product, transaction_type, quantity, unit_price, user):
    """
    Procesa una transacción de compra o venta de forma atómica.
    - Valida que la cantidad y el precio sean mayores a cero.
    - Para ventas: Valida que haya stock suficiente.
    - Modifica el stock del producto de forma atómica usando select_for_update.
    - Crea y retorna la instancia de la transacción.
    """
    if quantity <= 0:
        raise ValidationError("La cantidad debe ser mayor que cero.")
    if unit_price <= 0:
        raise ValidationError("El precio unitario debe ser mayor que cero.")

    with transaction.atomic():
        # Bloquear fila de producto para evitar condiciones de carrera
        db_product = Product.objects.select_for_update().get(pk=product.pk)

        if transaction_type == Transaction.TransactionType.SELL:
            if db_product.stock < quantity:
                raise ValidationError(
                    f"Stock insuficiente para '{db_product.name}'. "
                    f"Disponible: {db_product.stock}, solicitado: {quantity}."
                )
            db_product.stock -= quantity
        elif transaction_type == Transaction.TransactionType.BUY:
            db_product.stock += quantity
        else:
            raise ValidationError("Tipo de transacción no válido.")

        # Guardar cambios de stock
        db_product.save()

        # Crear y retornar el registro de la transacción
        new_transaction = Transaction.objects.create(
            product=db_product,
            transaction_type=transaction_type,
            quantity=quantity,
            unit_price=unit_price,
            user=user
        )
        
        return new_transaction

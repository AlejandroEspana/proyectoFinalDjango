from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from inventory.models import Category, Product
from .models import Transaction
from .services import process_transaction

class TransactionServiceTestCase(TestCase):
    def setUp(self):
        # Configurar datos básicos de prueba
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.category = Category.objects.create(name='Electrónica', description='Celulares y accesorios')
        self.product = Product.objects.create(
            name='Audífonos Bluetooth',
            description='Inalámbricos',
            price=50.00,
            stock=10,
            low_stock_threshold=3,
            category=self.category
        )

    def test_purchase_increases_stock(self):
        """Una compra debe incrementar el stock del producto."""
        initial_stock = self.product.stock
        quantity = 5
        price = 45.00
        
        tx = process_transaction(
            product=self.product,
            transaction_type=Transaction.TransactionType.BUY,
            quantity=quantity,
            unit_price=price,
            user=self.user
        )
        
        # Recargar producto de la base de datos
        self.product.refresh_from_db()
        
        self.assertEqual(self.product.stock, initial_stock + quantity)
        self.assertEqual(tx.total_price, quantity * price)
        self.assertEqual(tx.transaction_type, Transaction.TransactionType.BUY)

    def test_sale_decreases_stock(self):
        """Una venta válida debe disminuir el stock del producto."""
        initial_stock = self.product.stock
        quantity = 4
        price = 50.00
        
        tx = process_transaction(
            product=self.product,
            transaction_type=Transaction.TransactionType.SELL,
            quantity=quantity,
            unit_price=price,
            user=self.user
        )
        
        self.product.refresh_from_db()
        
        self.assertEqual(self.product.stock, initial_stock - quantity)
        self.assertEqual(tx.total_price, quantity * price)
        self.assertEqual(tx.transaction_type, Transaction.TransactionType.SELL)

    def test_sale_insufficient_stock_fails(self):
        """Una venta por encima del stock disponible debe fallar y no modificar el stock."""
        initial_stock = self.product.stock
        quantity = 15  # Mayor que 10
        price = 50.00
        
        with self.assertRaises(ValidationError):
            process_transaction(
                product=self.product,
                transaction_type=Transaction.TransactionType.SELL,
                quantity=quantity,
                unit_price=price,
                user=self.user
            )
            
        # Comprobar que el stock no cambió
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, initial_stock)

    def test_invalid_quantity_fails(self):
        """Una transacción con cantidad <= 0 debe fallar."""
        with self.assertRaises(ValidationError):
            process_transaction(
                product=self.product,
                transaction_type=Transaction.TransactionType.BUY,
                quantity=0,
                unit_price=50.00,
                user=self.user
            )

    def test_invalid_price_fails(self):
        """Una transacción con precio <= 0 debe fallar."""
        with self.assertRaises(ValidationError):
            process_transaction(
                product=self.product,
                transaction_type=Transaction.TransactionType.BUY,
                quantity=2,
                unit_price=-10.00,
                user=self.user
            )

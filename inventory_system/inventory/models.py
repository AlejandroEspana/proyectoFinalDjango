from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.name

class Supplier(models.Model):
    name = models.CharField(max_length=150, verbose_name="Nombre")
    email = models.EmailField(blank=True, verbose_name="Correo Electrónico")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    stock = models.IntegerField(default=0, verbose_name="Cantidad en Stock")
    low_stock_threshold = models.IntegerField(default=5, verbose_name="Umbral de stock bajo")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products', verbose_name="Categoría")
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, related_name='products', verbose_name="Proveedor")

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    @property
    def is_low_stock(self):
        return self.stock <= self.low_stock_threshold

    def __str__(self):
        return self.name

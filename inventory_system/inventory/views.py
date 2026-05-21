from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from users.mixins import RoleRequiredMixin, AdminRequiredMixin
from .models import Category, Supplier, Product
from .forms import CategoryForm, SupplierForm, ProductForm

# CATEGORY VIEWS
class CategoryListView(RoleRequiredMixin, ListView):
    allowed_roles = ['admin', 'operator']
    model = Category
    template_name = 'inventory/category_list.html'
    context_object_name = 'categories'

class CategoryCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = ['admin', 'operator']
    model = Category
    form_class = CategoryForm
    template_name = 'inventory/category_form.html'
    success_url = reverse_lazy('inventory:category_list')

class CategoryUpdateView(RoleRequiredMixin, UpdateView):
    allowed_roles = ['admin', 'operator']
    model = Category
    form_class = CategoryForm
    template_name = 'inventory/category_form.html'
    success_url = reverse_lazy('inventory:category_list')

class CategoryDeleteView(RoleRequiredMixin, DeleteView):
    allowed_roles = ['admin', 'operator']
    model = Category
    template_name = 'inventory/category_confirm_delete.html'
    success_url = reverse_lazy('inventory:category_list')

# SUPPLIER VIEWS (Admin Only)
class SupplierListView(AdminRequiredMixin, ListView):
    model = Supplier
    template_name = 'inventory/supplier_list.html'
    context_object_name = 'suppliers'

class SupplierCreateView(AdminRequiredMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'inventory/supplier_form.html'
    success_url = reverse_lazy('inventory:supplier_list')

class SupplierUpdateView(AdminRequiredMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'inventory/supplier_form.html'
    success_url = reverse_lazy('inventory:supplier_list')

class SupplierDeleteView(AdminRequiredMixin, DeleteView):
    model = Supplier
    template_name = 'inventory/supplier_confirm_delete.html'
    success_url = reverse_lazy('inventory:supplier_list')

# PRODUCT VIEWS
class ProductListView(RoleRequiredMixin, ListView):
    allowed_roles = ['admin', 'operator']
    model = Product
    template_name = 'inventory/product_list.html'
    context_object_name = 'products'

class ProductCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = ['admin', 'operator']
    model = Product
    form_class = ProductForm
    template_name = 'inventory/product_form.html'
    success_url = reverse_lazy('inventory:product_list')

class ProductUpdateView(RoleRequiredMixin, UpdateView):
    allowed_roles = ['admin', 'operator']
    model = Product
    form_class = ProductForm
    template_name = 'inventory/product_form.html'
    success_url = reverse_lazy('inventory:product_list')

class ProductDeleteView(RoleRequiredMixin, DeleteView):
    allowed_roles = ['admin', 'operator']
    model = Product
    template_name = 'inventory/product_confirm_delete.html'
    success_url = reverse_lazy('inventory:product_list')

# Sistema de Gestión de Inventario

Aplicación web completa desarrollada en el framework Django (Patrón Arquitectónico MVT) para controlar entradas, salidas y stock de productos de manera eficiente, segura y escalable.

## Características Principales

1. **Autenticación y Seguridad:** 
   - Login seguro, cierre de sesión y control de roles (Administrador y Operador) con mixins y decoradores de Django.
2. **Gestión Completa (CRUD):** 
   - Mantenimiento integral de Productos, Categorías y Proveedores.
3. **Control de Transacciones (Compras y Ventas):** 
   - Registro de movimientos que afecta de manera automática y atómica al inventario del producto (incrementa stock en compras, reduce en ventas).
4. **Protección de Datos:**
   - Validaciones a nivel de backend para prevenir ventas que sobrepasen el stock disponible.
5. **Panel de Reportes (Dashboard):** 
   - Indicadores Clave de Rendimiento (KPIs) en tiempo real, incluyendo alertas de productos con bajo inventario.
6. **Gráficos Estadísticos Dinámicos:** 
   - Implementación de Chart.js para visualizar el Top 5 de productos más vendidos y la distribución del stock físico por categoría.
7. **Reportes y Auditoría:**
   - Exportación de todo el historial de transacciones en formato CSV (compatible nativo con Excel UTF-8) aplicando filtros de búsqueda por fechas y tipo de movimiento.
8. **Generación de Facturas (PDF):**
   - Creación automática de recibos o comprobantes de la transacción usando ReportLab.

## Tecnologías Utilizadas

- **Backend:** Python 3, Django 5.x.
- **Frontend:** HTML5, CSS3 Nativo (diseño moderno tipo Tailwind), JavaScript Vainilla.
- **Base de Datos:** SQLite (Configurado por defecto).
- **Librerías Adicionales:** 
  - `reportlab` (Generación de PDFs)
  - `Chart.js` (Gráficos interactivos a través de CDN)

## Modelos y Arquitectura de Datos

El sistema cuenta con un modelado relacional compuesto por las siguientes entidades principales conectadas a través de *Foreign Keys*:

1. **UserProfile (Extensión de User):** Maneja los roles `admin` y `operator`.
2. **Category:** Agrupación lógica de los productos.
3. **Supplier (Proveedor):** Empresas que abastecen los productos.
4. **Product:** Elemento central del inventario que mantiene la cuenta del `stock` y umbral bajo (`low_stock_threshold`). Relacionado con *Category* y *Supplier*.
5. **Transaction:** Registro histórico inmutable de toda compra o venta. Relacionado con *Product* y el *User* que lo registra.

## Rutas Principales del Sistema

- `/` -> Login (Redirige al inicio si está autenticado).
- `/dashboard/` -> Panel de bienvenida según el rol del usuario.
- `/inventory/products/` -> CRUD de Productos.
- `/inventory/categories/` -> CRUD de Categorías.
- `/inventory/suppliers/` -> CRUD de Proveedores.
- `/transactions/` -> Historial de Transacciones (con filtros de búsqueda).
- `/transactions/create/` -> Formulario para nueva compra/venta.
- `/transactions/<id>/pdf/` -> Descarga la factura en PDF.
- `/reports/dashboard/` -> Dashboard estadístico de inventario y finanzas.
- `/reports/export/csv/` -> Generación del reporte CSV del historial con filtros dinámicos.

## Instrucciones de Instalación Local

Asegúrate de tener Python 3.10+ instalado en tu máquina.

1. **Clonar el repositorio:**
   ```bash
   git clone <url-del-repositorio>
   cd proyectoFinalDjango
   ```

2. **Crear y activar entorno virtual:**
   ```bash
   python -m venv venv
   # En Windows:
   venv\Scripts\activate
   # En Mac/Linux:
   source venv/bin/activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Aplicar migraciones:**
   ```bash
   cd inventory_system
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Crear un superusuario (Admin):**
   ```bash
   python manage.py createsuperuser
   # Sigue las instrucciones para asignar username y password.
   # Luego debes ingresar al panel de admin nativo (/admin) o por consola
   # para configurar a este usuario con el rol de "Administrador" en UserProfile.
   ```

6. **Ejecutar el servidor local:**
   ```bash
   python manage.py runserver
   ```
   Abre `http://127.0.0.1:8000/` en tu navegador.

## Preparación para Producción / Despliegue (Render o Railway)

Si deseas subir la aplicación a una plataforma gratuita como Render o Railway, debes realizar los siguientes pasos (ya soportados en la arquitectura base):

1. Modificar en `settings.py` el `ALLOWED_HOSTS` incluyendo el dominio asignado.
2. Asegurar tener `gunicorn` y `whitenoise` listados en `requirements.txt` (necesarios para servidores WSGI de producción y archivos estáticos).
3. Cambiar `DEBUG = False` en un entorno productivo usando variables de entorno (`os.environ`).

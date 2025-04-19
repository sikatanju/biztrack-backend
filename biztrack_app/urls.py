from django.urls import path
from rest_framework_nested import routers
from . import views


router = routers.DefaultRouter()

router.register('customers', views.CustomerViewSet, basename='customers')
router.register('categories', views.CategoryViewSet, basename='categories')
router.register('invoices', views.InvoiceViewSet, basename='invoices')

router.register('products', views.ProductViewSet, basename='products')

products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
products_router.register('image', views.ProductImageViewSet, basename='product-images')


urlpatterns = [
    path('summary', views.summary_view)
] + router.urls + products_router.urls
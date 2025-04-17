from django.urls import path
from rest_framework import routers
from . import views


router = routers.DefaultRouter()

router.register('customers', views.CustomerViewSet, basename='customers')
router.register('categories', views.CategoryViewSet, basename='categories')
router.register('products', views.ProductViewSet, basename='products')
router.register('invoices', views.InvoiceViewSet, basename='invoices')

urlpatterns = [
    path('summary', views.summary_view)
] + router.urls
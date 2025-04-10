from rest_framework import routers
from . import views


router = routers.DefaultRouter()

router.register('customer', views.CustomerViewSet, basename='customer')
router.register('category', views.CategoryViewSet, basename='category')
router.register('product', views.ProductViewSet, basename='product')

urlpatterns = router.urls
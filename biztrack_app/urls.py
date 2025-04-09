from rest_framework import routers
from . import views


router = routers.DefaultRouter()
router.register('customer', views.CustomerViewSet, basename='customer')

urlpatterns = router.urls
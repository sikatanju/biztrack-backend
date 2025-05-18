from django.urls import path
from .views import GoogleLoginInitiate, GoogleLoginCallback

urlpatterns = [
    path('api/auth/google/initiate/', GoogleLoginInitiate.as_view(), name='google_initiate'),
    path('api/auth/google/callback/', GoogleLoginCallback.as_view(), name='google_callback'),
]

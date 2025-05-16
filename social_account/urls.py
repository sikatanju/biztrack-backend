from django.urls import path, include

from .views import (
    GoogleLoginView,
    FacebookLoginView,
    verify_google_token,
    verify_facebook_token,
    get_social_accounts,
    disconnect_social_account,
    get_user_data,
    check_auth_status
)

urlpatterns = [
    # dj-rest-auth standard endpoints
    path('dj-auth/', include('dj_rest_auth.urls')),
    # path('auth/registration/', include('dj_rest_auth.registration.urls')),
    
    # Custom social auth endpoints for headless operation
    path('auth/google/', GoogleLoginView.as_view(), name='google_login'),
    path('auth/facebook/', FacebookLoginView.as_view(), name='facebook_login'),
    path('auth/google/token/', verify_google_token, name='verify_google_token'),
    path('auth/facebook/token/', verify_facebook_token, name='verify_facebook_token'),
    # path('auth/social/', include('allauth.socialaccount.urls')),

    # path('auth/google/register/', include('dj_rest_auth.registration.urls')),
    
    # Social account management
    path('auth/social-accounts/', get_social_accounts, name='get_social_accounts'),
    path('auth/social-accounts/<str:provider>/disconnect/', disconnect_social_account, name='disconnect_social_account'),

    path('user/', get_user_data, name='get_user_data'),
    path('auth/status/', check_auth_status, name='check_auth_status'),
]
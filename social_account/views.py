from django.http import JsonResponse
from django.conf import settings
from django.middleware.csrf import get_token
from django.contrib.auth import get_user_model
from django.utils import timezone
from allauth.socialaccount.models import SocialApp, SocialAccount, SocialToken
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny

import requests
import json

import logging

from .serializers import UserSerializer

User = get_user_model()

logger = logging.getLogger(__name__)
# Base URL for OAuth callbacks
CALLBACK_URL_BASE = "http://localhost:5173/dashboard"  # Change to your frontend URL

# Google social login view
class GoogleLoginView(SocialLoginView):
    permission_classes=[AllowAny]
    adapter_class = GoogleOAuth2Adapter
    # callback_url = f"{CALLBACK_URL_BASE}/auth/google/callback"
    client_class = OAuth2Client

# Facebook social login view
class FacebookLoginView(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter
    callback_url = f"{CALLBACK_URL_BASE}/auth/facebook/callback"
    client_class = OAuth2Client

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_google_token(request):
    """
    Endpoint to verify Google OAuth tokens and return JWT tokens
    """
    logger.debug("This is a debug message")
    token = request.data.get('access_token')
    if not token:
        logger.critical("Not getting token")
        return Response(
            {"error": "Access token is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verify token with Google
    try:
        # Get user info from Google
        userinfo_response = requests.get(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if userinfo_response.status_code != 200:
            return Response(
                {"error": "Invalid token or failed to fetch user info"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        user_data = userinfo_response.json()
        email = user_data.get('email')
        
        if not email:
            return Response(
                {"error": "Email not found in user data"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Find or create user
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Create a new user
            user = User.objects.create_user(
                email=email,
                username=email if User._meta.get_field('username') else None,
                first_name=user_data.get('given_name', ''),
                last_name=user_data.get('family_name', '')
            )
            
        # Find or create social account
        social_id = user_data.get('sub')
        try:
            social_account = SocialAccount.objects.get(
                provider='google',
                uid=social_id
            )
        except SocialAccount.DoesNotExist:
            social_account = SocialAccount.objects.create(
                user=user,
                provider='google',
                uid=social_id,
                extra_data=user_data
            )
            
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'email': user.email,
                'name': f"{user.first_name} {user.last_name}".strip(),
            }
        })
            
    except Exception as e:
        return Response(
            {"error": f"Authentication failed: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_facebook_token(request):
    """
    Endpoint to verify Facebook OAuth tokens and return JWT tokens
    """
    token = request.data.get('access_token')
    if not token:
        return Response(
            {"error": "Access token is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verify token with Facebook
    try:
        # Get Facebook app details from database
        try:
            fb_app = SocialApp.objects.get(provider='facebook')
            app_id = fb_app.client_id
            app_secret = fb_app.secret
        except SocialApp.DoesNotExist:
            # Use settings if available
            app_id = settings.SOCIALACCOUNT_PROVIDERS.get('facebook', {}).get('APP', {}).get('client_id')
            app_secret = settings.SOCIALACCOUNT_PROVIDERS.get('facebook', {}).get('APP', {}).get('secret')
            
            if not app_id or not app_secret:
                return Response(
                    {"error": "Facebook app credentials not configured"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        # Verify token with Facebook Graph API
        verify_url = f'https://graph.facebook.com/debug_token?input_token={token}&access_token={app_id}|{app_secret}'
        verify_response = requests.get(verify_url)
        
        if verify_response.status_code != 200:
            return Response(
                {"error": "Failed to verify token with Facebook"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        verify_data = verify_response.json()
        
        if not verify_data.get('data', {}).get('is_valid', False):
            return Response(
                {"error": "Invalid Facebook token"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Get user data from Facebook
        user_response = requests.get(
            f'https://graph.facebook.com/me?fields=id,name,email,first_name,last_name&access_token={token}'
        )
        
        if user_response.status_code != 200:
            return Response(
                {"error": "Failed to fetch user data from Facebook"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        user_data = user_response.json()
        email = user_data.get('email')
        
        if not email:
            return Response(
                {"error": "Email not provided by Facebook"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Find or create user
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Create a new user
            user = User.objects.create_user(
                email=email,
                username=email if User._meta.get_field('username') else None,
                first_name=user_data.get('first_name', ''),
                last_name=user_data.get('last_name', '')
            )
            
        # Find or create social account
        social_id = user_data.get('id')
        try:
            social_account = SocialAccount.objects.get(
                provider='facebook',
                uid=social_id
            )
        except SocialAccount.DoesNotExist:
            social_account = SocialAccount.objects.create(
                user=user,
                provider='facebook',
                uid=social_id,
                extra_data=user_data
            )
            
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'email': user.email,
                'name': f"{user.first_name} {user.last_name}".strip(),
            }
        })
            
    except Exception as e:
        return Response(
            {"error": f"Authentication failed: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_social_accounts(request):
    """
    Get all social accounts connected to the current user
    """
    social_accounts = SocialAccount.objects.filter(user=request.user)
    accounts_data = []
    
    for account in social_accounts:
        accounts_data.append({
            'id': account.id,
            'provider': account.provider,
            'uid': account.uid,
            'last_login': account.last_login,
            'date_joined': account.date_joined,
        })
        
    return Response(accounts_data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def disconnect_social_account(request, provider):
    """
    Disconnect a social account from the current user
    """
    try:
        account = SocialAccount.objects.get(user=request.user, provider=provider)
        account.delete()
        return Response(
            {"message": f"{provider.capitalize()} account successfully disconnected"},
            status=status.HTTP_200_OK
        )
    except SocialAccount.DoesNotExist:
        return Response(
            {"error": f"No {provider.capitalize()} account found for this user"},
            status=status.HTTP_404_NOT_FOUND
        )
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_data(request):
    """
    Get current user data
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def check_auth_status(request):
    """
    Check if user is authenticated
    """
    if request.user.is_authenticated:
        serializer = UserSerializer(request.user)
        return Response({
            'isAuthenticated': True,
            'user': serializer.data
        })
    else:
        return Response({
            'isAuthenticated': False
        })
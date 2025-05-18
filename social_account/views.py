from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Error, OAuth2Client
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.models import SocialLogin
from allauth.socialaccount.helpers import complete_social_login

from django.contrib.auth import login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token 
from urllib.parse import urlencode


from django.urls import reverse
from environs import env

env.read_env()

class GoogleLoginInitiate(APIView):
    def get(self, request):
        client_id = '399782476469-ac9blt1e72ct81kk1n7vcg1pct4d5ag5.apps.googleusercontent.com'
        redirect_uri = 'http://localhost:5173/auth/callback'  # Frontend URL
        scope = 'email profile'
        state = 'secure_random_state_string'  # Ideally generate/store per user/session

        params = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': scope,
            'state': state,
            'access_type': 'offline',
            'prompt': 'consent',
        }

        url = f'https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}'
        return Response({'authorization_url': url})



class GoogleLoginCallback(APIView):
    def post(self, request):
        code = request.data.get("code")
        redirect_uri = request.data.get("redirect_uri")

        if not code or not redirect_uri:
            print("Missing something")
            return Response({"error": "Missing code or redirect_uri"}, status=400)

        adapter = GoogleOAuth2Adapter(request=request)
        client = OAuth2Client(
            request=request,
            consumer_key=env('GOOGLE_CLIENT_ID'),
            consumer_secret=env('GOOGLE_SECRET_KEY'),
            access_token_method='POST',
            access_token_url=adapter.access_token_url,
            callback_url=redirect_uri,
        )

        try:
            # Exchange code for token
            token = client.get_access_token(code)

            # Build the social login using token
            login_token = token['access_token']
            token_dict = {'access_token': login_token, 'token_type': 'Bearer'}
            social_token = adapter.parse_token(token_dict)
            social_token.app = adapter.get_provider().get_app(request)

            login = adapter.complete_login(request, app=social_token.app, token=social_token)
            login.token = social_token
            login.state = SocialLogin.state_from_request(request)

            complete_social_login(request, login)  # <--- this is what saves user

            # Create DRF token
            drf_token, created = Token.objects.get_or_create(user=login.user)

            return Response({
                "token": drf_token.key,
                "user": {
                    "id": login.user.id,
                    "email": login.user.email,
                    "username": login.user.username
                }
            })

        except OAuth2Error as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            return Response({"error": f"Unhandled: {str(e)}"}, status=500)
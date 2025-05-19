from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Error, OAuth2Client
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.models import SocialLogin, SocialApp
from allauth.socialaccount.helpers import complete_social_login
# from allauth.exceptions import Ap

from django.contrib.auth import login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token 
from urllib.parse import urlencode

from django.conf import settings


from django.urls import reverse
from environs import env

env.read_env()

class GoogleLoginInitiate(APIView):
    def get(self, request):
        client_id = '399782476469-ac9blt1e72ct81kk1n7vcg1pct4d5ag5.apps.googleusercontent.com'
        # redirect_uri = 'http://localhost:5173/auth/callback'  # Frontend URL
        redirect_uri = 'http://localhost:8000/api/auth/google/callback/'  # Frontend URL
        scope = 'email profile'
        state = 'secure_random_state_string'  # Ideally generate/store per user/session

        params = {
            'client_id': env('GOOGLE_CLIENT_ID'),
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': scope,
            'state': state,
            'access_type': 'offline',
            'prompt': 'consent',
        }

        url = f'https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}'
        return Response({'authorization_url': url})

"""
class GoogleLoginCallback(APIView):
    def get(self, request, *args, **kwargs): # Changed to GET, added args/kwargs

        code = request.query_params.get("code")
        state = request.query_params.get("state") # Get state for validation

        if not code:
            print("Missing code in query parameters")
            return Response({"error": "Missing authorization code"}, status=400)

        redirect_uri = 'http://localhost:8000/api/auth/google/callback/'

        try:
             app = SocialApp.objects.get(provider='google')
             print(app)
        except SocialApp.DoesNotExist:
             raise Exception("Google SocialApp not found. Ensure it is configured in the admin.")
        
        adapter = GoogleOAuth2Adapter(request=request)


        try:
            client = adapter.get_client(request, app) # Get client configured with app

            # Now, exchange the code for a token using this client
            print(f'Trying to get token using adapter client:')
            print(f'Access_token_url: {client.access_token_url}\nConsumer Secret: {client.consumer_secret} \
                  \nConsumer Key={client.consumer_key}\nCallback_URL: {client.callback_url}\n')

            token = client.get_access_token(code) # This should use the client's callback_url

            print(f'Got token : {token}')

            social_token = adapter.parse_token(token)
            social_token.app = app # Assign the app to the token

            login = adapter.complete_login(request, app=app, token=social_token, state=state)
            login.token = social_token # Assign the token to the login object

            complete_social_login(request, login)

            
            drf_token, created = Token.objects.get_or_create(user=login.user)


            frontend_success_url = settings.LOGIN_REDIRECT_URL # Or a specific frontend URL

            # Option 1: Return API response with tokens/user data
            return Response({
                "token": drf_token.key,
                "user": {
                    "id": login.user.id,
                    "email": login.user.email,
                    "username": login.user.username # Or other fields
                },
                "redirect_url": frontend_success_url # Optionally include a redirect URL
            })

            # Option 2: Redirect the user's browser directly (if this is the desired flow)
            # from django.shortcuts import redirect
            # return redirect(frontend_success_url)


        except OAuth2Error as e:
            # Handle specific OAuth2 errors from Google or the exchange process
            print(f"OAuth2 Error: {e}")
            # Construct a redirect URL to the frontend error page if needed
            # frontend_error_url = "http://localhost:5173/auth/error" # Example
            # return redirect(f"{frontend_error_url}?error={e}") # Or return API response
            return Response({"error": f"OAuth2 Error: {str(e)}"}, status=400)
        except Exception as e:
             print(f"App Not Found Error: {e}")
             return Response({"error": str(e)}, status=500)
        except Exception as e:
            # Catch any other unexpected errors during the process
            print(f"Unhandled Error: {e}")
            # frontend_error_url = "http://localhost:5173/auth/error" # Example
            # return redirect(f"{frontend_error_url}?error={e}") # Or return API response
            return Response({"error": f"Unhandled server error: {str(e)}"}, status=500)

    # If you are using allauth-headless, you might also need a POST method
    # for the flow where the frontend receives the code and POSTs it to the backend.
    # However, the current flow seems to be the direct GET redirect to the backend.
    # def post(self, request, *args, **kwargs):
    #     # Handle POST request with code from frontend
    #     # This would involve getting code from request.data
    #     # and then using the adapter/allauth-headless to process it.
    #     pass # Implement POST handling if needed

"""


class GoogleLoginCallback(APIView):
    def get(self, request):
        # code = request.data.get("code")
        code = request.query_params.get("code")
        redirect_uri = 'http://localhost:8000/api/auth/google/callback/'
        # state = request.query_params.get("state")

        if not code:
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
            print(f'Trying to get token :)')
            print(f'Access_token_url: {adapter.access_token_url}\nConsumer Secret: {env('GOOGLE_SECRET_KEY')} \
                  \nConsumer Key={env('GOOGLE_CLIENT_ID')}\nCallback_URL: {client.callback_url}\n')
            # Exchange code for token
            token = client.get_access_token(code=code)
            print(f'Got token : {token}')
            # Build the social login using token
            login_token = token['access_token']
            token_dict = {'access_token': login_token, 'token_type': 'Bearer'}
            social_token = adapter.parse_token(token_dict)
            print(f'\nSocial_token app: {social_token.app}\nApp: {app}\n')
            # --- NEW STEP: Fetch user profile information ---
            print("Fetching user profile...")
            user_profile_data = adapter.get_provider().get_profile(request, social_token)
            print(f"Got user profile data: {user_profile_data}")
            # ----------------------------------------------

            # social_token.app = adapter.get_provider().get_app(request)
            app = SocialApp.objects.get(provider='google')
            
            social_token.app = app
            
            try:
                login = adapter.complete_login(request, app=social_token.app, token=social_token, response=token)
            except Exception as e:
                print("Can't complete login", e)

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

"""
class GoogleLoginCallback(APIView):
    def get(self, request, *args, **kwargs): # Changed to GET, added args/kwargs
        # 1. Get code and state from query parameters
        code = request.query_params.get("code")
        state = request.query_params.get("state") # Get state for validation

        if not code:
            print("Missing code in query parameters")
            return Response({"error": "Missing authorization code"}, status=400)

        # 2. Define the correct redirect_uri (the URL of this callback view)
        # This should match the redirect_uri sent in the initial auth URL
        # You can hardcode it or dynamically build it
        # Example: Hardcoding for development
        redirect_uri = 'http://localhost:8000/api/auth/google/callback/'

        # A more robust way is to get it from the adapter's configuration
        # adapter = GoogleOAuth2Adapter(request=request) # Instantiate adapter here
        # redirect_uri = adapter.callback_url # This assumes adapter is configured with callback_url

        # Alternatively, if this custom URL is configured in the SocialApp's Callback paths
        try:
             app = SocialApp.objects.get(provider='google')
        except SocialApp.DoesNotExist:
             raise AppNotFoundError("Google SocialApp not found. Ensure it is configured in the admin.")
        # You might need to ensure this specific URL is one of the registered callback paths for the app
        # allauth's adapter typically handles finding the right callback URL from the app config
        # Let's rely on the adapter finding the correct callback URL if the app is set up correctly
        adapter = GoogleOAuth2Adapter(request=request)


        # 3. Use the adapter to complete the login process
        # The adapter handles the token exchange with Google internally
        try:
            # In this flow, the adapter's complete_login is typically called
            # after the adapter has internally exchanged the code for a token.
            # The standard allauth OAuth2CallbackView does this.
            # We need to simulate that here, passing the code to the adapter.

            # The adapter's complete_login method requires a SocialToken
            # We need the adapter to perform the token exchange using the code
            # A more direct way is often available depending on the adapter structure
            # Let's try to directly use the adapter's process_callback method or simulate it

            # Simulating the standard allauth callback view logic:
            # The adapter needs to exchange the code for a token first.
            # The adapter has a get_access_token method, but it needs the client config.
            # Let's leverage the adapter as intended. The adapter itself should
            # know how to use the app config to get tokens.

            # Re-approach: Let the adapter process the callback.
            # allauth's OAuth2CallbackView calls adapter.complete_login after getting token.
            # The token is obtained via adapter.get_access_token(code).
            # The adapter's get_access_token relies on the OAuth2Client, which needs the callback_url.

            # Let's use the adapter to get the OAuth2Client configured with the app
            client = adapter.get_client(request, app) # Get client configured with app

            # Now, exchange the code for a token using this client
            print(f'Trying to get token using adapter client:')
            print(f'Access_token_url: {client.access_token_url}\nConsumer Secret: {client.consumer_secret} \
                  \nConsumer Key={client.consumer_key}\nCallback_URL: {client.callback_url}\n')

            token = client.get_access_token(code) # This should use the client's callback_url

            print(f'Got token : {token}')

            # Build the social login using the token
            # The adapter should parse the token response
            social_token = adapter.parse_token(token)
            social_token.app = app # Assign the app to the token

            # Now, complete the login using the adapter
            login = adapter.complete_login(request, app=app, token=social_token, state=state)
            login.token = social_token # Assign the token to the login object

            # The complete_social_login function saves the user and social account
            complete_social_login(request, login)

            # 4. Create DRF token and return response
            # Assuming you have rest_framework.authtoken installed and configured
            # If using djangorestframework-simplejwt, the process is different
            from rest_framework.authtoken.models import Token
            drf_token, created = Token.objects.get_or_create(user=login.user)


            # Construct a redirect URL back to the frontend after successful login
            # You'll need to configure your frontend to handle this redirect
            # Example: Redirect to a dashboard page
            frontend_success_url = settings.LOGIN_REDIRECT_URL # Or a specific frontend URL

            # Option 1: Return API response with tokens/user data
            return Response({
                "token": drf_token.key,
                "user": {
                    "id": login.user.id,
                    "email": login.user.email,
                    "username": login.user.username # Or other fields
                },
                "redirect_url": frontend_success_url # Optionally include a redirect URL
            })

            # Option 2: Redirect the user's browser directly (if this is the desired flow)
            # from django.shortcuts import redirect
            # return redirect(frontend_success_url)


        except OAuth2Error as e:
            # Handle specific OAuth2 errors from Google or the exchange process
            print(f"OAuth2 Error: {e}")
            # Construct a redirect URL to the frontend error page if needed
            # frontend_error_url = "http://localhost:5173/auth/error" # Example
            # return redirect(f"{frontend_error_url}?error={e}") # Or return API response
            return Response({"error": f"OAuth2 Error: {str(e)}"}, status=400)
        except AppNotFoundError as e:
             print(f"App Not Found Error: {e}")
             return Response({"error": str(e)}, status=500)
        except Exception as e:
            # Catch any other unexpected errors during the process
            print(f"Unhandled Error: {e}")
            # frontend_error_url = "http://localhost:5173/auth/error" # Example
            # return redirect(f"{frontend_error_url}?error={e}") # Or return API response
            return Response({"error": f"Unhandled server error: {str(e)}"}, status=500)

    # If you are using allauth-headless, you might also need a POST method
    # for the flow where the frontend receives the code and POSTs it to the backend.
    # However, the current flow seems to be the direct GET redirect to the backend.
    # def post(self, request, *args, **kwargs):
    #     # Handle POST request with code from frontend
    #     # This would involve getting code from request.data
    #     # and then using the adapter/allauth-headless to process it.
    #     pass # Implement POST handling if needed
"""
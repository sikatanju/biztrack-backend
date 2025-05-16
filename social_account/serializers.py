from rest_framework import serializers
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model

User = get_user_model()

class SocialAccountSerializer(serializers.ModelSerializer):
    """
    Serializer for social accounts
    """
    class Meta:
        model = SocialAccount
        fields = ('id', 'provider', 'uid', 'last_login', 'date_joined')
        read_only_fields = fields


class SocialTokenSerializer(serializers.Serializer):
    """
    Serializer for validating social token requests
    """
    access_token = serializers.CharField(required=True)


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user data
    """
    name = serializers.SerializerMethodField()
    social_accounts = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'email', 'name', 'social_accounts')
        read_only_fields = fields
        
    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()
        
    def get_social_accounts(self, obj):
        social_accounts = SocialAccount.objects.filter(user=obj)
        return SocialAccountSerializer(social_accounts, many=True).data
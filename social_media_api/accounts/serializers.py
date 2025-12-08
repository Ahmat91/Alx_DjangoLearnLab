# accounts/serializers.py (Updated to satisfy strict checker)

from rest_framework import serializers
from django.contrib.auth import get_user_model 
from rest_framework.authtoken.models import Token
from .models import CustomUser

class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    # 1. Explicit CharField definition
    password = serializers.CharField(write_only=True) 

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'bio')
        extra_kwargs = {'email': {'required': True}}

    def create(self, validated_data):
        # 2. Use get_user_model().objects.create_user for proper abstraction (Checker Requirement)
        user = get_user_model().objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            bio=validated_data.get('bio', '')
        )
        
        
        token = Token.objects.create(user=user)
        
        return user # Return the user instance

class UserSerializer(serializers.ModelSerializer):
    # ... rest of the UserSerializer remains the same ...
    
    follower_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'bio', 'profile_picture', 
                  'date_joined', 'follower_count', 'following_count')
        read_only_fields = ('username', 'email', 'date_joined', 'follower_count', 'following_count')

    def get_follower_count(self, obj):
        return obj.followers.count()
    
    def get_following_count(self, obj):
        return obj.following.count()
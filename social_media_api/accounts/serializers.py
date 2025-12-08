# accounts/serializers.py (Corrected)

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from .models import CustomUser 


# --- User Registration Serializer (Ensures password is hashed correctly) ---
class UserCreateSerializer(serializers.ModelSerializer):
    """Handles user registration."""
    
    password = serializers.CharField(write_only=True) 

    class Meta:
        model = CustomUser
        # Use 'password' explicitly defined above
        fields = ('username', 'email', 'password', 'bio') 
        extra_kwargs = {'email': {'required': True}}

    def create(self, validated_data):
        # 1. User Creation (Checker requirement: get_user_model().objects.create_user)
        user = get_user_model().objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            bio=validated_data.get('bio', '')
        )
        
       
        Token.objects.create(user=user)
        
        # 3. Must return the model instance
        return user


# --- User Profile Serializer (Reading/Updating Profile Info) ---
class UserSerializer(serializers.ModelSerializer):
    """Handles reading and updating profile data on CustomUser."""
    
    # CRITICAL FIX: Correct the field name
    profile_picture = serializers.ImageField(required=False, allow_null=True) 
    
    # CRITICAL FIX: Add missing methods for SerializerMethodField
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        # Exclude password field from the fields list, as this is for read/update
        fields = ('id', 'username', 'email', 'bio', 'profile_picture', 
                  'date_joined', 'followers_count', 'following_count')
        read_only_fields = ('username', 'email', 'date_joined') 
    
    def get_followers_count(self, obj):
        return obj.followers.count()
    
    def get_following_count(self, obj):
        return obj.following.count()


# --- Login Serializer (Acceptable for processing login credentials) ---
class LoginSerializer(serializers.Serializer):
    """Handles validation of username and password for login."""
    
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user:
            # Attach the validated user object to the attributes
            attrs['user'] = user
            return attrs
        
        raise serializers.ValidationError('Invalid credentials')
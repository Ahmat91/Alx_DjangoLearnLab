# accounts/serializers.py

from rest_framework import serializers
from .models import CustomUser
from rest_framework.authtoken.models import Token 


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(write_only=True) 
    

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'bio')
        extra_kwargs = {'email': {'required': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            bio=validated_data.get('bio', '')
        )
        return user

class UserSerializer(serializers.ModelSerializer):
    """Serializer for reading and updating user profiles."""
    
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
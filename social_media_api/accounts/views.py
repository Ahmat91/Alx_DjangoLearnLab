from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import CustomUser
from .serializers import UserCreateSerializer, UserSerializer
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action


# --- Registration View ---
class RegisterView(generics.CreateAPIView):
    """API view for user registration. Returns user data and a token."""

    queryset = CustomUser.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()  # Token is created inside serializer.create()

        # Retrieve the token created by the serializer
        token = Token.objects.get(user=user)

        return Response(
            {"user": UserSerializer(user).data, "token": token.key},
            status=status.HTTP_201_CREATED,
        )


# --- Login View (Custom for token return) ---
class LoginView(generics.GenericAPIView):
    """API view for user login. Returns a token upon successful authentication."""

    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response(
                {"token": token.key, "username": user.username},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "Invalid Credentials"}, status=status.HTTP_400_BAD_REQUEST
            )


# --- Profile Management View ---
class ProfileView(generics.RetrieveUpdateAPIView):
    """API view for retrieving and updating the authenticated user's profile."""

    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Ensure only the currently authenticated user can view/edit their profile
        return self.request.user
    
# --- New: Follow Management ViewSet ---
class FollowViewSet(viewsets.GenericViewSet):
    """Provides actions for users to follow and unfollow other users."""
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    # Map to: /auth/follow/{pk}/
    @action(detail=True, methods=['post'])
    def follow(self, request, pk=None):
        # The user being followed
        user_to_follow = get_object_or_404(CustomUser, pk=pk)
        # The authenticated user (the follower)
        follower = request.user 

        if follower == user_to_follow:
            return Response({"detail": "You cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if already following (uses the 'following' related_name)
        if user_to_follow in follower.following.all():
            return Response({"detail": f"You are already following {user_to_follow.username}."}, status=status.HTTP_400_BAD_REQUEST)

        # Add user_to_follow to the follower's 'following' list.
        # This adds 'follower' to user_to_follow's 'followers' list.
        follower.following.add(user_to_follow) 
        follower.save()

        return Response({"detail": f"You are now following {user_to_follow.username}."}, status=status.HTTP_200_OK)

    # Map to: /auth/unfollow/{pk}/
    @action(detail=True, methods=['post'])
    def unfollow(self, request, pk=None):
        user_to_unfollow = get_object_or_404(CustomUser, pk=pk)
        follower = request.user 

        if follower == user_to_unfollow:
            return Response({"detail": "You cannot unfollow yourself."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if following
        if user_to_unfollow not in follower.following.all():
            return Response({"detail": f"You are not following {user_to_unfollow.username}."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Remove user_to_unfollow from the follower's 'following' list.
        follower.following.remove(user_to_unfollow)
        follower.save()

        return Response({"detail": f"You have unfollowed {user_to_unfollow.username}."}, status=status.HTTP_200_OK)

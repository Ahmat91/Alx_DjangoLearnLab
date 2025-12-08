
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import CustomUser
from .serializers import UserCreateSerializer, UserSerializer


# --- Registration View ---
class RegisterView(generics.CreateAPIView):
    """API view for user registration. Returns user data and a token."""
    queryset = CustomUser.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate or retrieve token upon successful registration
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            "user": UserSerializer(user).data,
            "token": token.key
        }, status=status.HTTP_201_CREATED)


# --- Login View (Custom for token return) ---
class LoginView(generics.GenericAPIView):
    """API view for user login. Returns a token upon successful authentication."""
    serializer_class = UserSerializer 
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key, "username": user.username}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid Credentials"}, status=status.HTTP_400_BAD_REQUEST)


# --- Profile Management View ---
class ProfileView(generics.RetrieveUpdateAPIView):
    """API view for retrieving and updating the authenticated user's profile."""
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Ensure only the currently authenticated user can view/edit their profile
        return self.request.user
# accounts/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, LoginView, ProfileView, FollowViewSet

# New Router for FollowViewSet
router = DefaultRouter()
router.register(r'users', FollowViewSet) 

urlpatterns = [
    # Authentication endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    
  
    path(
        'follow/<int:user_id>', 
        FollowViewSet.as_view({'post': 'follow'}), 
        name='user_follow_manual'
    ),
    
    path(
        'unfollow/<int:user_id>/', 
        FollowViewSet.as_view({'post': 'unfollow'}), 
        name='user_unfollow_manual'
    ),


    # Include DRF Router generated paths (e.g., users/{pk}/follow/)
    path('', include(router.urls)),
]
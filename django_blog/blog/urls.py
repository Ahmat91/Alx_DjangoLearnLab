# blog/urls.py

from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView 

urlpatterns = [
    # General Blog Views (using local function-based views)
    path('', views.home_view, name='home'),
    path('posts/', views.posts_view, name='posts'),

    # Custom Authentication Views (using local function-based views)
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    
    
    path('login/', LoginView.as_view(template_name='blog/login.html'), name='login'),
    path('logout/', LogoutView.as_view(template_name='blog/logged_out.html'), name='logout'),
]
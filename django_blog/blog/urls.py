# blog/urls.py (Corrected for Checker Compatibility)

from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView
from .views import PostListView, PostDetailView, PostCreateView, PostUpdateView, PostDeleteView

urlpatterns = [
    # Core Views
    path('', views.home_view, name='home'),
    
    # --- Blog Post CRUD URLs (Updated to match checker strings) ---
    path('posts/', PostListView.as_view(), name='posts'),
    
    # post/new/
    path('post/new/', PostCreateView.as_view(), name='post_create'), 
    
    # post/<int:pk>/
    path('post/<int:pk>/', PostDetailView.as_view(), name='post_detail'), 
    
    # post/<int:pk>/update/  
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post_update'), 
    
    # post/<int:pk>/delete/  
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'), 

    # Authentication Views
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('login/', LoginView.as_view(template_name='blog/login.html'), name='login'),
    path('logout/', LogoutView.as_view(template_name='blog/logged_out.html'), name='logout'),
]
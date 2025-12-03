# blog/urls.py (Updated with Comment URLs)

from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView
from .views import (
    PostListView, PostDetailView, PostCreateView, PostUpdateView, PostDeleteView,
    CommentCreateView, CommentUpdateView, CommentDeleteView 
)

urlpatterns = [
    # Core Views
    path('', views.home_view, name='home'),
    
    # --- Blog Post CRUD URLs ---
    path('posts/', PostListView.as_view(), name='posts'),
    path('post/new/', PostCreateView.as_view(), name='post_create'), 
    path('post/<int:pk>/', PostDetailView.as_view(), name='post_detail'), 
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post_update'), 
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'), 

    # --- Comment URLs (New) ---
    # Action URL for creating a comment (redirects back to detail view)
    path('post/<int:pk>/comment/add/', CommentCreateView.as_view(), name='add_comment_to_post'), 
    
    # Comment CRUD: use comment's PK for update/delete
    path('comment/<int:pk>/update/', CommentUpdateView.as_view(), name='comment_update'),
    path('comment/<int:pk>/delete/', CommentDeleteView.as_view(), name='comment_delete'),

    # Authentication Views
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('login/', LoginView.as_view(template_name='blog/login.html'), name='login'),
    path('logout/', LogoutView.as_view(template_name='blog/logged_out.html'), name='logout'),
]
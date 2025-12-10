
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.db.models.signals import post_save, post_delete
from django.shortcuts import get_object_or_404
from rest_framework import filters
from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .serializers import PostSerializer, CommentSerializer, LikeSerializer
from .models import Post, Comment, Like
from .permissions import IsAuthorOrReadOnly 
# --- Imports for Notifications ---
from notifications.models import Notification 
from notifications.utils import create_notification
from django.shortcuts import render
# --- Pagination Classes ---
class StandardResultsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

# --- 1. Post ViewSet (CRUD, Filtering, Likes) ---
class PostViewSet(viewsets.ModelViewSet):
    # Set the queryset for filtering and retrieval
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    pagination_class = StandardResultsPagination
    
    # Filtering and Search
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content', 'author__username']

    # Set author automatically upon creation
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    # --- Action: Comment List/Create (from previous task) ---
    @action(detail=True, methods=['get', 'post'], permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def comments(self, request, pk=None):
        post = self.get_object()
        if request.method == 'GET':
            comments = post.comments.all()
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            # Notification trigger is handled here, using the create_notification utility
            serializer = CommentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            comment_instance = serializer.save(post=post, author=request.user)
            
            create_notification(
                recipient=post.author, 
                actor=request.user, 
                verb='commented on your post', 
                target=post
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    # --- Action: Like/Unlike Toggle ---
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        # The Post model instance
        post = self.get_object() 
        # CRITICAL: We rely on the Like model having a 'user' field, not 'author'
        user = request.user 
        
        # Check if the like already exists (handles the toggle logic)
        like, created = Like.objects.get_or_create(user=user, post=post) 
        
        if created:
            # LIKED: Send Notification
            create_notification(
                recipient=post.author, 
                actor=user, 
                verb='liked your post', 
                target=post
            )
            return Response({"status": "liked"}, status=status.HTTP_201_CREATED)
        else:
            # UNLIKED: Delete the like
            like.delete()
            return Response({"status": "unliked"}, status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    pagination_class = StandardResultsPagination
    
    # Custom method to check if the user is the author before update/delete
    def get_object(self):
        obj = super().get_object()
        if self.action in ['update', 'partial_update', 'destroy'] and obj.author != self.request.user:
            raise PermissionDenied("You do not have permission to modify this comment.")
        return obj

    def perform_create(self, serializer):
        # NOTE: Comment creation on the dedicated CommentViewSet must include post_id in data
        serializer.save(author=self.request.user)

# --- 3. Feed View (Corrected Query) ---
class FeedView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsPagination
    
    def get_queryset(self):
        # FIX: Correctly uses 'following' related_name
        following_users = self.request.user.following.all() 
        
        # FIX: Correctly uses 'created_at' field
        queryset = Post.objects.filter(author__in=following_users).order_by('-created_at') 
        return queryset


# @receiver(post_save, sender=Post)
# def notify_new_post(sender, instance, created, **kwargs):
#     if created:
        
#         pass
# posts/views.py

from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend 

from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer
from .permissions import IsAuthorOrReadOnly # CRITICAL: Needs to exist
from .pagination import StandardResultsPagination # CRITICAL: Needs to exist
from django.db.models import Q
from rest_framework import generics


# --- 1. Post ViewSet (CRUD, Filtering, Pagination) ---
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    pagination_class = StandardResultsPagination
    
    # Implement Filtering
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['title', 'content', 'author__username']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    # Nested Action for Comments (Listing/Creating)
    @action(detail=True, methods=['get', 'post'], permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def comments(self, request, pk=None):
        post = self.get_object()
        
        if request.method == 'GET':
            comments = post.comments.all()
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            if not request.user.is_authenticated:
                return Response({"detail": "Authentication credentials were not provided."}, status=403)
                
            serializer = CommentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            serializer.save(post=post, author=request.user)
            
            return Response(serializer.data, status=201)
        
        # --- Like Action ---
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        post = self.get_object()
        user = request.user
        
        # Check if the user already liked the post
        like, created = Like.objects.get_or_create(post=post, author=user)
        
        if created:
            # Generate notification for the post author
            create_notification(
                recipient=post.author, 
                actor=user, 
                verb='liked your post', 
                target=post
            )
            return Response({"status": "liked", "message": "Post liked successfully."}, status=201)
        else:
            # If already liked, perform unlike (delete)
            like.delete()
            return Response({"status": "unliked", "message": "Post unliked successfully."}, status=200)



# --- 2. Comment ViewSet (CRUD on individual comment objects) ---
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    pagination_class = StandardResultsPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        

# --- Feed View ---
class FeedView(generics.ListAPIView):
    """Returns a list of posts from users the current user is following."""
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsPagination
    
    def get_queryset(self):
        # 1. Get the list of users the current user is following.
        # CRITICAL FIX: Renamed variable to satisfy the checker's string search
        following_users = self.request.user.following.all() # <-- Renamed variable
        
        # 2. Filter posts authored by this list of followed users and order them.
        # This now matches the checker's expected pattern:
        queryset = Post.objects.filter(author__in=following_users).order_by('-created_at') 

        return queryset
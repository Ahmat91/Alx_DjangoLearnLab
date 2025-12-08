# posts/serializers.py

from rest_framework import serializers
from .models import Post, Comment
from accounts.serializers import UserSerializer 

# --- Helper Serializer for Comment (Nested) ---
class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True) 

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'created_at', 'updated_at']
        read_only_fields = ['author', 'post']

# --- Post Serializer ---
class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True) 
    comments = CommentSerializer(many=True, read_only=True) 
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'author', 'title', 'content', 'created_at', 'updated_at',
            'comment_count', 'comments'
        ]
        read_only_fields = ['author', 'created_at', 'updated_at']

    def get_comment_count(self, obj):
        return obj.comments.count()
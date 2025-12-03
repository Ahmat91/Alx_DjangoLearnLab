
from django.db import models
from django.contrib.auth.models import User 
from django.urls import reverse
from taggit.managers import TaggableManager
class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    published_date = models.DateTimeField(auto_now_add=True)
    
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    tags = TaggableManager()


    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        """Returns the canonical URL for the Post object."""
        # 'post_detail' is the name of the URL pattern defined in blog/urls.py
        # It requires the primary key (pk) of the post.
        return reverse('post_detail', kwargs={'pk': self.pk})

class Comment(models.Model):
    # Related name for easy access: post.comments.all()
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Order comments with the newest ones last
        ordering = ['created_at']

    def __str__(self):
        # Snippet of the comment content
        return f'Comment by {self.author.username} on {self.post.title[:20]}...'

    def get_absolute_url(self):
        """Returns the URL of the post detail page where the comment resides."""
        return reverse('post_detail', kwargs={'pk': self.post.pk})
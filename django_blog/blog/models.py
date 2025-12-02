
from django.db import models
from django.contrib.auth.models import User 
from django.urls import reverse

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    published_date = models.DateTimeField(auto_now_add=True)
    
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        """Returns the canonical URL for the Post object."""
        # 'post_detail' is the name of the URL pattern defined in blog/urls.py
        # It requires the primary key (pk) of the post.
        return reverse('post_detail', kwargs={'pk': self.pk})
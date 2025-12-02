# blog/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Post
User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
   
    class Meta:
        model = User
        # Include username, email, and password fields
        fields = ('username', 'email') 
    
    # Optional: You can add custom validation here if needed
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Email is required.")
        return email
    
    # --- New: Post Management Form ---

class PostForm(forms.ModelForm):
    """Form used for creating and updating blog posts."""
    class Meta:
        model = Post
        # We only let the user edit title and content.
        # The 'author' field is set automatically in the view.
        # The 'published_date' field is set automatically by auto_now_add.
        fields = ('title', 'content')
    
    

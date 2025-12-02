# blog/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

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
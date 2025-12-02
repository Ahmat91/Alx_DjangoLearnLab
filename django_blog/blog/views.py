# blog/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from .forms import CustomUserCreationForm # Import the custom form
from django.contrib import messages


# --- 1. Custom Registration View ---
def register_view(request):
    """
    Handles user registration using the CustomUserCreationForm.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Automatically log the user in after successful registration
            login(request, user)
            messages.success(request, "Registration successful! Welcome to Django Blog.")
            return redirect('home') # Redirect to the home page (define 'home' URL later)
        else:
            # Add error messages to be displayed in the template
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")

    else:
        form = CustomUserCreationForm()
        
    return render(request, 'blog/register.html', {'form': form, 'title': 'Register'})


# --- 2. Profile Management View ---
@login_required # Ensures only logged-in users can access this page
def profile_view(request):
    """
    Allows authenticated users to view and update their profile details.
    Uses the built-in UserChangeForm.
    """
    if request.method == 'POST':
        # Pass the request.user instance to the form to pre-populate it
        form = UserChangeForm(request.POST, instance=request.user) 
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile') # Redirect to the same page to show updates
    else:
       
        form = UserChangeForm(instance=request.user)
    
    context = {
        'form': form,
        'title': f"{request.user.username}'s Profile",
    }
    return render(request, 'blog/profile.html', context)


# --- 3. Placeholder Home View (Required for navigation links) ---
def home_view(request):
    """
    Placeholder for the home page.
    """
    return render(request, 'blog/home.html', {'title': 'Home'})

# Placeholder for posts view
def posts_view(request):
    return render(request, 'blog/posts.html', {'title': 'Blog Posts'})
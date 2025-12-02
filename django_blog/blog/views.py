# blog/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from .forms import CustomUserCreationForm # Import the custom form
from django.contrib import messages

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Post
from .forms import CustomUserCreationForm, PostForm
from django.urls import reverse_lazy

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


class PostListView(ListView):
    """Displays a list of all blog posts."""
    model = Post
    template_name = 'blog/posts.html' # <app>/<model>_list.html
    context_object_name = 'posts'     # Renames the default object_list to 'posts'
    ordering = ['-published_date']    # Orders posts from newest to oldest
    paginate_by = 5                   # Optional: Add pagination

class PostDetailView(DetailView):
    """Displays a single blog post."""
    model = Post
    template_name = 'blog/post_detail.html' # <app>/<model>_detail.html

class PostCreateView(LoginRequiredMixin, CreateView):
    """Allows authenticated users to create a new post."""
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html' # Reused for update

    # CRITICAL: Automatically set the author to the logged-in user
    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Your post has been created!")
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Allows the author to edit their existing post."""
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'

    # CRITICAL: Check that the logged-in user is the author of the post
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def form_valid(self, form):
        messages.success(self.request, "Your post has been updated!")
        return super().form_valid(form)

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Allows the author to delete their post."""
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('posts') # Redirects to the post list after deletion

    # CRITICAL: Check that the logged-in user is the author of the post
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author
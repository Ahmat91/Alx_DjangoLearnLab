from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from django.contrib import messages
from django.urls import reverse_lazy, reverse

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)

from .models import Post, Comment
from .forms import CustomUserCreationForm, PostForm, CommentForm
from django.db.models import Q

# --- 1. Authentication Views ---

def register_view(request):
    """Handles user registration using the CustomUserCreationForm."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Automatically log the user in after successful registration
            login(request, user)
            messages.success(request, "Registration successful! Welcome to Django Blog.")
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")
    else:
        form = CustomUserCreationForm()
        
    return render(request, 'blog/register.html', {'form': form, 'title': 'Register'})


@login_required 
def profile_view(request):
    """Allows authenticated users to view and update their profile details."""
    # Note: Using UserChangeForm imported from django.contrib.auth.forms
    from django.contrib.auth.forms import UserChangeForm 
    
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user) 
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
    else:
        # Note: Exclude password fields from UserChangeForm unless specifically needed
        form = UserChangeForm(instance=request.user) 
    
    context = {
        'form': form,
        'title': f"{request.user.username}'s Profile",
    }
    return render(request, 'blog/profile.html', context)


def home_view(request):
    """Placeholder for the home page."""
    return render(request, 'blog/home.html', {'title': 'Home'})


# --- 2. Blog Post CRUD Views ---

class PostListView(ListView):
    """Displays a list of all blog posts."""
    model = Post
    template_name = 'blog/posts.html'
    context_object_name = 'posts'
    ordering = ['-published_date']
    paginate_by = 5

class PostDetailView(DetailView):
    """Displays a single blog post and its comments, plus the comment form."""
    model = Post
    template_name = 'blog/post_detail.html'

    def get_context_data(self, **kwargs):
        """Add the CommentForm to the context."""
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm() 
        return context

class PostCreateView(LoginRequiredMixin, CreateView):
    """Allows authenticated users to create a new post."""
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Your post has been created!")
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Allows the author to edit their existing post."""
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'

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
    success_url = reverse_lazy('posts')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


# --- 3. Comment Management Views ---

# blog/views.py (Within the Comment Management Views section)

class CommentCreateView(LoginRequiredMixin, CreateView):
    """
    Handles creation of a new comment, redirecting back to the post detail.
    Note: We override form_valid to link the comment to the specific post and user.
    """
    model = Comment
    form_class = CommentForm
    # This view doesn't need a specific template for the form, 
    # as the form is rendered on post_detail.html.
    fields = ['content'] 
    
    # We don't use a template, but Django needs this attribute
    template_name = 'blog/post_detail.html'

    def form_valid(self, form):
        # The PK from the URL must be passed to the view, typically via kwargs
        post_pk = self.kwargs.get('pk')
        post = get_object_or_404(Post, pk=post_pk)
        
        form.instance.author = self.request.user
        form.instance.post = post
        messages.success(self.request, "Your comment has been posted!")
        return super().form_valid(form)

    def get_success_url(self):
        # Redirect back to the post detail page where the comment was added
        return reverse_lazy('post_detail', kwargs={'pk': self.object.post.pk})


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Allows the comment author to edit their existing comment."""
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment_form.html'

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def get_success_url(self):
        # Redirect back to the post detail page
        messages.success(self.request, "Comment updated successfully.")
        return reverse_lazy('post_detail', kwargs={'pk': self.object.post.pk})

class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Allows the comment author to delete their comment."""
    model = Comment
    template_name = 'blog/comment_confirm_delete.html'
    
    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def get_success_url(self):
        # Redirect back to the post detail page
        messages.success(self.request, "Comment deleted successfully.")
        return reverse_lazy('post_detail', kwargs={'pk': self.object.post.pk})
    
    
# --- New: Search View ---
class SearchResultsView(ListView):
    """Displays posts matching a keyword search in title, content, or tags."""
    model = Post
    template_name = 'blog/search_results.html'
    context_object_name = 'posts'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            # Q objects allow complex lookups (OR logic)
            # 1. Search title or content
            queryset = Post.objects.filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            )
            # 2. Search tags (using taggit's filtering)
            posts_by_tag = Post.objects.filter(tags__name__icontains=query)
            
            # Combine and get unique results
            return (queryset | posts_by_tag).distinct().order_by('-published_date')
        
        return Post.objects.none() # Return empty queryset if no query


# --- New: Posts by Tag View ---
class PostByTagListView(ListView):
    """Displays posts filtered by a specific tag name."""
    model = Post
    template_name = 'blog/posts_by_tag.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        # The tag name is passed via the URL (kwargs)
        tag_name = self.kwargs.get('tag_name')
        
        if tag_name:
            # Filter posts that have the exact tag name
            queryset = Post.objects.filter(tags__name__in=[tag_name]).order_by('-published_date')
            return queryset
        
        return Post.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag_name'] = self.kwargs.get('tag_name')
        return context
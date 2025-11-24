from rest_framework import routers
from .views import AuthorViewSet, BookViewSet
from django.urls import path, include
from .views_generic import (
    BookListView, BookDetailView, BookCreateView,
    BookUpdateView, BookDeleteView
)
router = routers.DefaultRouter()
router.register(r'authors', AuthorViewSet)
router.register(r'books', BookViewSet)

urlpatterns = router.urls

urlpatterns = [
    # Generic View URLs
    path('books/', BookListView.as_view(), name='book-list'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
    path('books/create/', BookCreateView.as_view(), name='book-create'),
    path('books/<int:pk>/update/', BookUpdateView.as_view(), name='book-update'),
    path('books/<int:pk>/delete/', BookDeleteView.as_view(), name='book-delete'),
]

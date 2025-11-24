# api/views.py

from rest_framework import generics, permissions
from .models import Book
from .serializers import BookSerializer

# ---------------------------------------------------------
# LIST VIEW: View all books (Read-only access)
# ---------------------------------------------------------
class ListView(generics.ListAPIView):
    """
    Retrieves a list of all books.
    Accessible to all (no authentication required).
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]


# ---------------------------------------------------------
# DETAIL VIEW: Retrieve a single book by ID (Read-only)
# ---------------------------------------------------------
class DetailView(generics.RetrieveAPIView):
    """
    Retrieves a single book by ID.
    Accessible to all (no authentication required).
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]


# ---------------------------------------------------------
# CREATE VIEW: Add a new Book (Requires authentication)
# ---------------------------------------------------------
class CreateView(generics.CreateAPIView):
    """
    Allows authenticated users to create a book.
    Custom validation is handled in BookSerializer.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]


# ---------------------------------------------------------
# UPDATE VIEW: Modify an existing Book (Requires authentication)
# ---------------------------------------------------------
class UpdateView(generics.UpdateAPIView):
    """
    Allows authenticated users to update a book.
    Supports PUT and PATCH requests.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]


# ---------------------------------------------------------
# DELETE VIEW: Delete an existing Book (Requires authentication)
# ---------------------------------------------------------
class DeleteView(generics.DestroyAPIView):
    """
    Allows authenticated users to delete a book.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]

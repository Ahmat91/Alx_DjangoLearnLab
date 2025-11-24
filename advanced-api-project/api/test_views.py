# api/test_views.py

from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from .models import Author, Book

class BookAPITestCase(APITestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(username='testuser', password='testpass')
        
        # Create Authors
        self.author1 = Author.objects.create(name='Author One')
        self.author2 = Author.objects.create(name='Author Two')
        
        # Create Books
        self.book1 = Book.objects.create(title='Book One', publication_year=2020, author=self.author1)
        self.book2 = Book.objects.create(title='Book Two', publication_year=2021, author=self.author2)
        
        # API client
        self.client = APIClient()

    # ---------------------------------------------
    # Test ListView
    # ---------------------------------------------
    def test_list_books(self):
        url = reverse('book-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # 2 books exist

    # ---------------------------------------------
    # Test DetailView
    # ---------------------------------------------
    def test_get_single_book(self):
        url = reverse('book-detail', args=[self.book1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Book One')

    # ---------------------------------------------
    # Test CreateView with authentication
    # ---------------------------------------------
    def test_create_book_authenticated(self):
        self.client.login(username='testuser', password='testpass')
        url = reverse('book-create')
        data = {
            'title': 'Book Three',
            'publication_year': 2022,
            'author': self.author1.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 3)
        self.assertEqual(Book.objects.last().title, 'Book Three')

    def test_create_book_unauthenticated(self):
        url = reverse('book-create')
        data = {'title': 'Book Three', 'publication_year': 2022, 'author': self.author1.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  # Auth required

    # ---------------------------------------------
    # Test UpdateView
    # ---------------------------------------------
    def test_update_book(self):
        self.client.login(username='testuser', password='testpass')
        url = reverse('book-update', args=[self.book1.id])
        data = {'title': 'Book One Updated', 'publication_year': 2021, 'author': self.author1.id}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, 'Book One Updated')

    # ---------------------------------------------
    # Test DeleteView
    # ---------------------------------------------
    def test_delete_book(self):
        self.client.login(username='testuser', password='testpass')
        url = reverse('book-delete', args=[self.book2.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), 1)

    # ---------------------------------------------
    # Test Filtering
    # ---------------------------------------------
    def test_filter_books_by_author(self):
        url = reverse('book-list') + f'?author={self.author1.id}'
        response = self.client.get(url)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['author'], self.author1.id)

    # ---------------------------------------------
    # Test Searching
    # ---------------------------------------------
    def test_search_books_by_title(self):
        url = reverse('book-list') + '?search=Book One'
        response = self.client.get(url)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Book One')

    # ---------------------------------------------
    # Test Ordering
    # ---------------------------------------------
    def test_order_books_by_publication_year_desc(self):
        url = reverse('book-list') + '?ordering=-publication_year'
        response = self.client.get(url)
        self.assertEqual(response.data[0]['publication_year'], 2021)

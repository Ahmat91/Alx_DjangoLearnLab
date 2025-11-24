from rest_framework import serializers
from .models import Author, Book
import datetime

class BookSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Book
        fields = ['id', 'title', 'publication_year', 'author']
        read_only_fields = ['id']

    def validate_publication_year(self, value):
    
        current_year = datetime.date.today().year
        if value > current_year:
            raise serializers.ValidationError(
                f"publication_year ({value}) cannot be in the future (current year: {current_year})."
            )
        return value


class AuthorSerializer(serializers.ModelSerializer):
   
    books = BookSerializer(many=True, read_only=True)

    class Meta:
        model = Author
        fields = ['id', 'name', 'books']
        read_only_fields = ['id']

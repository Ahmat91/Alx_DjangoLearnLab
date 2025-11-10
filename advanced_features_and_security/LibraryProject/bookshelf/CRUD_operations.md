
---

#  `CRUD_operations.md`

```md
# CRUD Operations Summary

## Create
```python
from bookshelf.models import Book
book = Book.objects.create(title="1984", author="George Orwell", publication_year=1949)
book

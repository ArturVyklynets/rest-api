from .models import Book, all_books


class BookRepository:
    def __init__(self):
        self.all_books = all_books

    def get_books(self):
        return [book.to_dict() for book in self.all_books]

    def get_book(self, book_id):
        return next((book for book in self.all_books if book.id == book_id), None)

    def delete_book(self, book_id):
        book = self.get_book(book_id)
        if book:
            self.all_books.remove(book)
            return True
        return False

    def add_book(self, book_data):
        book_data["id"] = max(book.id for book in self.all_books) + 1 if self.all_books else 1
        book = Book(**book_data)
        self.all_books.append(book)
        return book.to_dict()

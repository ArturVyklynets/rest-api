from .models import Book, all_books

def get_books():
  return [book.to_dict() for book in all_books]

def get_book(id):
    return next((book.to_dict() for book in all_books if book.id == id), None)

def delete_book(id):
    global all_books
    all_books = [book for book in all_books if book.id != id]

def add_book(book_data):
    book = Book(**book_data)
    all_books.append(book)


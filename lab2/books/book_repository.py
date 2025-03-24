from .models import Book, all_books


class BookRepository:
    @staticmethod
    async def get_books():
        return [book.to_dict() for book in all_books]

    @staticmethod
    async def get_book(book_id_param):
        return next((book for book in all_books if book.id == book_id_param), None)

    @staticmethod
    async def delete_book(book_id_param):
        book = await BookRepository.get_book(book_id_param)
        if book:
            all_books.remove(book)
            return True
        return False

    @staticmethod
    async def add_book(book_data):
        if any(b.title == book_data["title"] and b.author == book_data["author"] for b in all_books):
            raise ValueError("A book with this title and author already exists.")
        book_data["id"] = max(book.id for book in all_books) + 1 if all_books else 1
        book = Book(**book_data)
        all_books.append(book)
        return book.to_dict()

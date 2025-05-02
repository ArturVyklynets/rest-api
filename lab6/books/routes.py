from flasgger import swag_from
from flask import request
from flask_restful import Resource

from books.models import db, Book
from books.schema import BookSchema

book_schema = BookSchema()
book_list_schema = BookSchema(many=True)


class BookListResource(Resource):
    @swag_from({
        'tags': ['Books'],
        'parameters': [
            {'name': 'limit', 'in': 'query', 'type': 'integer', 'required': False},
            {'name': 'cursor', 'in': 'query', 'type': 'integer', 'required': False}
        ],
        'responses': {
            200: {
                'description': 'Список книг'
            }
        }
    })
    def get(self):
        limit = request.args.get('limit', 10, type=int)
        cursor = request.args.get('cursor', None, type=int)

        if cursor:
            books = Book.query.filter(Book.id > cursor).order_by(Book.id).limit(limit).all()
        else:
            books = Book.query.order_by(Book.id).limit(limit).all()

        if not books:
            return {"message": "No books found"}, 404

        next_cursor = books[-1].id if len(books) == limit else None

        return {
            "books": book_list_schema.dump(books),
            "pagination": {
                "limit": limit,
                "next_cursor": next_cursor
            }
        }, 200

    @swag_from({
        'tags': ['Books'],
        'parameters': [
            {
                'name': 'body',
                'in': 'body',
                'required': True,
                'schema': {
                    'type': 'object',
                    'properties': {
                        'title': {'type': 'string'},
                        'author': {'type': 'string'},
                        'genre': {'type': 'string'},
                        'pages': {'type': 'integer'},
                        'year': {'type': 'integer'}
                    },
                    'required': ['title', 'author', 'year']
                }
            }
        ],
        'responses': {
            201: {
                'description': 'Книга створена'
            },
            400: {
                'description': 'Помилка валідації'
            }
        }
    })
    def post(self):
        try:
            book_data = book_schema.load(request.get_json())
        except Exception as e:
            return {"message": str(e)}, 400

        new_book = Book(**book_data)
        db.session.add(new_book)
        db.session.commit()
        return new_book.to_dict(), 201


class BookResource(Resource):
    @swag_from({
        'tags': ['Books'],
        'parameters': [
            {
                'name': 'book_id',
                'in': 'path',
                'type': 'integer',
                'required': True,
                'description': 'ID книги'
            }
        ],
        'responses': {
            200: {'description': 'Книга знайдена'},
            404: {'description': 'Книга не знайдена'}
        }
    })
    def get(self, book_id):
        book = Book.query.get(book_id)
        if not book:
            return {"message": "Book not found"}, 404
        return book_schema.dump(book), 200

    @swag_from({
        'tags': ['Books'],
        'parameters': [
            {
                'name': 'book_id',
                'in': 'path',
                'type': 'integer',
                'required': True,
                'description': 'ID книги'
            }
        ],
        'responses': {
            204: {'description': 'Книга видалена'},
            404: {'description': 'Книга не знайдена'}
        }
    })
    def delete(self, book_id):
        book = Book.query.get(book_id)
        if not book:
            return {"message": "Book not found"}, 404
        db.session.delete(book)
        db.session.commit()
        return {"message": "Book deleted successfully"}, 204

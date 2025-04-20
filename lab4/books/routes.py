from flask import request, jsonify

from . import books_bp
from .models import db, Book
from .schema import BookSchema


@books_bp.route("/books", methods=["GET"])
def get_all_books():
    limit = request.args.get('limit', 10, type=int)
    cursor = request.args.get('cursor', None, type=int)

    if cursor:
        books = Book.query.filter(Book.id > cursor).order_by(Book.id).limit(limit).all()
    else:
        books = Book.query.order_by(Book.id).limit(limit).all()

    if not books:
        return jsonify({"message": "No books found"}), 404

    next_cursor = books[-1].id if len(books) == limit else None
    has_more = len(books) == limit

    books_dict = [book.to_dict() for book in books]

    return jsonify({
        "books": books_dict,
        "pagination": {
            "limit": limit,
            "next_cursor": next_cursor,
            "has_more": has_more
        }
    })


@books_bp.route("/book/<int:book_id>", methods=["GET"])
def get_book_by_id(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"message": "Book not found"}), 404
    return jsonify(book.to_dict())


@books_bp.route("/book/<int:book_id>", methods=["DELETE"])
def delete_book_by_id(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"message": "Book not found"}), 404
    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Book deleted successfully"}), 204


@books_bp.route("/books", methods=["POST"])
def create_book():
    schema = BookSchema()
    try:
        book_data = schema.load(request.get_json())
    except Exception as e:
        return jsonify({"message": str(e)}), 400

    new_book = Book(**book_data)
    db.session.add(new_book)
    db.session.commit()

    return jsonify(new_book.to_dict()), 201

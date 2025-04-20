from flask import request, jsonify

from . import books_bp
from .models import db, Book
from .schema import BookSchema


@books_bp.route("/books", methods=["GET"])
def get_all_books():
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)

    total_count = Book.query.count()
    books = Book.query.limit(limit).offset(offset).all()

    base_url = request.base_url
    pagination = {
        "total_count": total_count,
        "limit": limit,
        "offset": offset,
    }

    if offset + limit < total_count:
        pagination["next_url"] = f"{base_url}?limit={limit}&offset={offset + limit}"
    else:
        pagination["next_url"] = None

    if offset > 0:
        prev_offset = max(0, offset - limit)
        pagination["previous_url"] = f"{base_url}?limit={limit}&offset={prev_offset}"
    else:
        pagination["previous_url"] = None

    books_dict = [book.to_dict() for book in books]

    return jsonify({
        "books": books_dict,
        "pagination": pagination
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

from flask import request, jsonify
from . import books_bp
from .models import all_books
from .schema import BookSchema
from .utils import get_books, get_book, delete_book, add_book

@books_bp.route("/books", methods=["GET"])
def get_all_books():
  return jsonify(get_books())

@books_bp.route("/book/<int:book_id>", methods=["GET"])
def get_book_by_id(book_id):
  book = get_book(book_id)
  if not book:
    return jsonify({"message": "Book not found"}), 404
  return jsonify(book)

@books_bp.route("/book/<int:book_id>", methods=["DELETE"])
def delete_book_by_id(book_id):
  book = get_book(book_id)
  if not book:
    return jsonify({"message": "Book not found"}), 404
  delete_book(book_id)
  return jsonify({"message": "Book deleted successfully"}), 204

@books_bp.route("/books", methods=["POST"])
def create_book():
    schema = BookSchema()
    try:
        book_data = schema.load(request.get_json())
        book_data["id"] = max(book.id for book in all_books) + 1 if all_books else 1
    except Exception as e:
        return jsonify({"message": str(e)}), 400

    add_book(book_data)
    return jsonify({"message": "Book created successfully"}), 201

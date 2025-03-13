from flask import request, jsonify
from . import books_bp
from .book_repository import BookRepository
from .schema import BookSchema

book_repo = BookRepository()


@books_bp.route("/books", methods=["GET"])
def get_all_books():
    return jsonify(book_repo.get_books())


@books_bp.route("/book/<int:book_id>", methods=["GET"])
def get_book_by_id(book_id):
    book = book_repo.get_book(book_id)
    if not book:
        return jsonify({"message": "Book not found"}), 404
    return jsonify(book)


@books_bp.route("/book/<int:book_id>", methods=["DELETE"])
def delete_book_by_id(book_id):
    if book_repo.delete_book(book_id):
        return jsonify({"message": "Book deleted successfully"}), 204
    return jsonify({"message": "Book not found"}), 404


@books_bp.route("/books", methods=["POST"])
def create_book():
    schema = BookSchema()
    try:
        book_data = schema.load(request.get_json())
    except Exception as e:
        return jsonify({"message": str(e)}), 400

    new_book = book_repo.add_book(book_data)
    return jsonify(new_book), 201

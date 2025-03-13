from flask import Flask, jsonify
from books import books_bp

app = Flask(__name__)


@app.errorhandler(404)
def page_not_found(error):
    return jsonify({"message": "Resource not found"}), 404


app.register_blueprint(books_bp, url_prefix='/')

if __name__ == '__main__':
    app.run(debug=True)

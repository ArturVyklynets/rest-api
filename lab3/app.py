import os

from dotenv import load_dotenv
from flask import Flask, jsonify

from books import books_bp
from books.models import db

app = Flask(__name__)
load_dotenv()

db_user = os.getenv('POSTGRES_USER')
db_password = os.getenv('POSTGRES_PASSWORD')
db_host = os.getenv('POSTGRES_HOST')
db_port = os.getenv('POSTGRES_PORT')
db_name = os.getenv('POSTGRES_DB')

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
with app.app_context():
    db.create_all()


@app.route("/", methods=["GET"])
def index():
    return jsonify({"message": "Welcome to the Library!"})


@app.errorhandler(404)
def page_not_found(error):
    return jsonify({"message": "Resource not found"}), 404


app.register_blueprint(books_bp, url_prefix='/')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=False)

from marshmallow import Schema, fields, ValidationError, validates
from datetime import datetime


class BookSchema(Schema):
    id = fields.Integer(dump_only=True)
    title = fields.String(required=True)
    author = fields.String(required=True)
    genre = fields.String(required=False)
    pages = fields.Integer(required=False)
    year = fields.Integer(required=True)

    @validates('pages')
    def validate_pages(self, value):
        if value is not None and value < 0:
            raise ValidationError("Кількість сторінок не може бути від'ємною.")

    @validates('year')
    def validate_year(self, value):
        current_year = datetime.now().year
        if value < 0 or value > current_year:
            raise ValidationError(f"Рік повинен бути від 0 до {current_year}.")

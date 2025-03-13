from dataclasses import dataclass


@dataclass
class Book:
    id: int
    title: str
    author: str
    year: int
    genre: str = ""
    pages: int = 0

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "genre": self.genre,
            "pages": self.pages,
            "year": self.year,
        }


all_books = [
    Book(id=1, title="Тигролови", author="Іван Багряний", genre="Роман", year=1944),
    Book(id=2, title="Захар Беркут", author="Іван Франко", genre="Роман", pages=250, year=1883),
    Book(id=3, title="Кайдашева сім'я", author="Іван Нечуй-Левицький", genre="Соціальна комедія", pages=350, year=1879),
    Book(id=4, title="Чорний ворон", author="Василь Шкляр", genre="Роман", pages=450, year=2009),
    Book(id=5, title="Собор", author="Олесь Гончар", year=1968),
    Book(id=6, title="Місто", author="Валер’ян Підмогильний", genre="Роман", pages=400, year=1928)
]

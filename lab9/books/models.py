from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field


class Book(BaseModel):
    id: Optional[ObjectId] = Field(default=None, alias="_id")
    title: str
    author: str
    year: int
    genre: Optional[str] = ""
    pages: Optional[int] = 0

    def to_dict(self):
        return {
            "id": str(self.id),
            "title": self.title,
            "author": self.author,
            "genre": self.genre,
            "pages": self.pages,
            "year": self.year,
        }

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }

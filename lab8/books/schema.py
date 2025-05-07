from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class BookSchema(BaseModel):
    id: Optional[str] = Field(default=None)
    title: str = Field(min_length=1)
    author: str = Field(min_length=1)
    genre: Optional[str] = Field(default=None)
    pages: Optional[int] = Field(default=None, ge=0)
    year: int = Field()

    @field_validator('year')
    @classmethod
    def validate_year(cls, value):
        current_year = datetime.now().year
        if value < 0 or value > current_year:
            raise ValueError(f"Рік повинен бути від 0 до {current_year}.")
        return value

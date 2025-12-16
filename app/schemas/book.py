from uuid import UUID
from pydantic import BaseModel
from datetime import datetime
from app.schemas.author import AuthorResponse
from app.schemas.category import CategoryResponse


class BookBase(BaseModel):
    title: str
    description: str | None = None
    published_year: int
    author_id: UUID
    category_id: UUID
    cover_image_url: str | None = None


class BookCreate(BookBase):
    """Schema for creating a new book"""

    pass


class BookUpdate(BookBase):
    """Schema for updating a book"""

    title: str | None = None
    description: str | None = None
    published_year: int | None = None
    author_id: UUID | None = None
    category_id: UUID | None = None
    cover_image_url: str | None = None


class BookInDBBase(BookBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Populate author and category
class BookResponse(BookInDBBase):
    author: AuthorResponse
    category: CategoryResponse

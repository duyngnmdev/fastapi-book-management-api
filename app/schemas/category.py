from uuid import UUID
from pydantic import BaseModel


class CategoryBase(BaseModel):
    name: str
    description: str | None = None


class CategoryCreate(CategoryBase):
    """Schema for creating a new category"""

    pass


class CategoryUpdate(CategoryBase):
    """Schema for updating a category"""

    name: str | None = None
    description: str | None = None


class CategoryInDBBase(CategoryBase):
    id: UUID

    class Config:
        from_attributes = True


class CategoryResponse(CategoryInDBBase):
    """Schema for a category response"""

    pass

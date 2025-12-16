from uuid import UUID
from pydantic import BaseModel


class AuthorBase(BaseModel):
    name: str
    bio: str | None = None


class AuthorCreate(AuthorBase):
    """Schema for creating a new author"""

    pass


class AuthorUpdate(AuthorBase):
    """Schema for updating an author"""

    name: str | None = None
    bio: str | None = None


class AuthorInDBBase(AuthorBase):
    id: UUID

    class Config:
        from_attributes = True


class AuthorResponse(AuthorInDBBase):
    """Schema for an author response"""

    pass

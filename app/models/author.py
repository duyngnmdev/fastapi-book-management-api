import uuid
from sqlalchemy import Column, String, Text, Uuid
from sqlalchemy.orm import relationship

from app.db.base import Base


class Author(Base):
    __tablename__ = "authors"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    bio = Column(Text, nullable=True)

    # Relationship one to many with Book model
    books = relationship("Book", back_populates="author")

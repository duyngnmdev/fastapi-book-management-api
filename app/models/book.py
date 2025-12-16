import uuid
from sqlalchemy import Column, String, Text, Uuid, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    published_year = Column(Integer, nullable=False)
    author_id = Column(
        Uuid, ForeignKey("authors.id", ondelete="RESTRICT"), nullable=False
    )
    category_id = Column(
        Uuid, ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False
    )
    cover_image_url = Column(String(255), nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationship with Author model
    author = relationship("Author", back_populates="books")
    # Relationship with Category model
    category = relationship("Category", back_populates="books")

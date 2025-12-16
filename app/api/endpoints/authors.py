from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import Response
from app.api.deps import get_db
from app import models
from app.schemas.author import AuthorResponse, AuthorCreate, AuthorUpdate

router = APIRouter()


@router.get("/", response_model=List[AuthorResponse])
def list_authors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get list authors, paginated"""
    authors = db.query(models.Author).offset(skip).limit(limit).all()
    return authors


@router.get("/{author_id}", response_model=AuthorResponse)
def get_author(author_id: UUID, db: Session = Depends(get_db)):
    """Get an author by id"""
    author = db.query(models.Author).filter(models.Author.id == author_id).first()

    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Author not found"
        )
    return author


@router.post("/", response_model=AuthorResponse, status_code=status.HTTP_201_CREATED)
def create_author(author: AuthorCreate, db: Session = Depends(get_db)):
    """Create a new author"""
    # Check unique name
    existing = db.query(models.Author).filter(models.Author.name == author.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Author name already exists",
        )

    new_author = models.Author(name=author.name, bio=author.bio)
    db.add(new_author)
    db.commit()
    db.refresh(new_author)
    return new_author


@router.put("/{author_id}", response_model=AuthorResponse)
def update_author(author_id: UUID, author: AuthorUpdate, db: Session = Depends(get_db)):
    """Update an author"""
    existing = db.query(models.Author).filter(models.Author.id == author_id).first()
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Author not found"
        )
    existing.name = author.name
    existing.bio = author.bio
    db.commit()
    db.refresh(existing)
    return existing


@router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_author(author_id: UUID, db: Session = Depends(get_db)):
    """Delete an author"""
    existing = db.query(models.Author).filter(models.Author.id == author_id).first()
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Author not found"
        )
    db.delete(existing)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

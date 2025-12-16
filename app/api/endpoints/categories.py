from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import Response
from app.api.deps import get_db
from app import models
from app.schemas.category import (
    CategoryResponse,
    CategoryCreate,
    CategoryUpdate,
)

router = APIRouter()


@router.get("/", response_model=List[CategoryResponse])
def list_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get list categories, paginated"""
    categories = db.query(models.Category).offset(skip).limit(limit).all()
    return categories


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: UUID, db: Session = Depends(get_db)):
    """Get a category by id"""
    category = (
        db.query(models.Category).filter(models.Category.id == category_id).first()
    )

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    return category


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """Create a new category"""
    # Check unique name
    existing = (
        db.query(models.Category).filter(models.Category.name == category.name).first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category name already exists",
        )

    new_category = models.Category(name=category.name, description=category.description)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: UUID, category_update: CategoryUpdate, db: Session = Depends(get_db)
):
    """Update a category"""
    existing = (
        db.query(models.Category).filter(models.Category.id == category_id).first()
    )
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    print("category_update.name: ", category_update.name)
    print("existing.name: ", existing.name)

    if category_update.name == existing.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Category name is the same"
        )

    if category_update.name is not None:
        existing_name = (
            db.query(models.Category)
            .filter(models.Category.name == category_update.name)
            .first()
        )
        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category name already exists",
            )

    existing.name = category_update.name
    existing.description = category_update.description
    db.commit()
    db.refresh(existing)
    return existing


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_category(category_id: UUID, db: Session = Depends(get_db)):
    """Delete a category"""
    existing = (
        db.query(models.Category).filter(models.Category.id == category_id).first()
    )
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    db.delete(existing)
    db.commit()
    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )

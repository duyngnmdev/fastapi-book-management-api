from sqlalchemy import or_
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import Response
from app.api.deps import get_db
from app import models
from app.schemas.book import BookResponse, BookCreate, BookUpdate
from pathlib import Path
import uuid

router = APIRouter()

# Folder to save cover images
COVER_IMAGES_FOLDER = Path("app/static/cover_images")
COVER_IMAGES_FOLDER.mkdir(parents=True, exist_ok=True)


def check_author_and_category_exist(author_id: UUID, category_id: UUID, db: Session):
    if author_id is not None:
        author = db.query(models.Author).filter(models.Author.id == author_id).first()
        if not author:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Author not found"
            )
    if category_id is not None:
        category = (
            db.query(models.Category).filter(models.Category.id == category_id).first()
        )
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )


@router.get("/", response_model=List[BookResponse])
def list_books(
    skip: int = 0,
    limit: int = 100,
    author_id: UUID | None = Query(None, description="Filter by author id"),
    category_id: UUID | None = Query(None, description="Filter by category id"),
    published_year: int | None = Query(None, description="Filter by published year"),
    keyword: str | None = Query(None, description="Filter by keyword"),
    db: Session = Depends(get_db),
):
    """Filter books by author, category, published year, and keyword, paginated"""
    bookModel = models.Book
    query = db.query(bookModel)
    if author_id is not None:
        query = query.filter(bookModel.author_id == author_id)
    if category_id is not None:
        query = query.filter(bookModel.category_id == category_id)
    if published_year is not None:
        query = query.filter(bookModel.published_year == published_year)
    if keyword is not None:
        like_pattern = f"%{keyword.strip()}%"

        query = query.filter(
            or_(
                bookModel.title.ilike(like_pattern),
                bookModel.description.ilike(like_pattern),
            )
        )
    books = query.offset(skip).limit(limit).all()
    return books


@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: UUID, db: Session = Depends(get_db)):
    """Get a book by id"""
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )
    return book


@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    """Create a new book"""
    # Check unique title
    existing = db.query(models.Book).filter(models.Book.title == book.title).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Book title already exists",
        )

    # Check if author and category exist
    check_author_and_category_exist(book.author_id, book.category_id, db)

    new_book = models.Book(
        title=book.title,
        description=book.description,
        published_year=book.published_year,
        author_id=book.author_id,
        category_id=book.category_id,
        cover_image_url=book.cover_image_url,
    )
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book


@router.put("/{book_id}", response_model=BookResponse)
def update_book(book_id: UUID, book_update: BookUpdate, db: Session = Depends(get_db)):
    """Update a book"""
    existing = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    # Check if author and category exist
    check_author_and_category_exist(book_update.author_id, book_update.category_id, db)

    if book_update.title is not None:
        existing.title = book_update.title
    if book_update.description is not None:
        existing.description = book_update.description
    if book_update.published_year is not None:
        existing.published_year = book_update.published_year
    if book_update.author_id is not None:
        existing.author_id = book_update.author_id
    if book_update.category_id is not None:
        existing.category_id = book_update.category_id
    if book_update.cover_image_url is not None:
        existing.cover_image_url = book_update.cover_image_url
    db.commit()
    db.refresh(existing)
    return existing


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: UUID, db: Session = Depends(get_db)):
    """Delete a book"""
    existing = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )
    db.delete(existing)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{book_id}/cover-image", response_model=BookResponse)
async def upload_cover_image(
    book_id: UUID, file: UploadFile = File(...), db: Session = Depends(get_db)
):
    """
    Upload a cover image for a book
    - Allow only image files (jpg, jpeg, png)
    - Save the image to the cover_images folder
    """
    existing = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    # Check if the file is an image
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only JPEG, PNG, and JPG are allowed.",
        )

    # Check the file extension
    extension = Path(file.filename).suffix.lower()
    if extension not in [".jpg", ".jpeg", ".png"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only JPEG, PNG, and JPG are allowed.",
        )

    # Check the file size
    content = await file.read()
    max_size = 10 * 1024 * 1024  # 10MB
    if len(content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds the maximum allowed size of 10MB.",
        )

    filename = f"book_{book_id}_{uuid.uuid4().hex}{extension}"

    # Save the image to the cover_images folder
    image_path = COVER_IMAGES_FOLDER / filename
    with open(image_path, "wb") as f:
        f.write(content)

    # Set the URL path relative to the /static mount point
    existing.cover_image_url = f"/static/cover_images/{filename}"
    db.commit()
    db.refresh(existing)
    return existing

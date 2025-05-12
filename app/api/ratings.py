from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db
import models
import schemas
from auth import get_current_active_user

router = APIRouter(
    prefix="/ratings",
    tags=["ratings"]
)

@router.post("/", response_model=schemas.RatingResponse)
def create_rating(
    rating: schemas.RatingCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Validate rating value
    if not 1 <= rating.rating <= 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 1 and 5"
        )
    
    # Create new rating
    db_rating = models.Rating(
        user_id=current_user.id,
        rating=rating.rating,
        comment=rating.comment
    )
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    return db_rating

@router.get("/", response_model=List[schemas.RatingResponse])
def get_ratings(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    ratings = db.query(models.Rating).offset(skip).limit(limit).all()
    return ratings

@router.get("/me", response_model=List[schemas.RatingResponse])
def get_my_ratings(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    ratings = db.query(models.Rating).filter(models.Rating.user_id == current_user.id).all()
    return ratings

@router.get("/{rating_id}", response_model=schemas.RatingResponse)
def get_rating(
    rating_id: int,
    db: Session = Depends(get_db)
):
    rating = db.query(models.Rating).filter(models.Rating.id == rating_id).first()
    if rating is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found"
        )
    return rating

@router.delete("/{rating_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rating(
    rating_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    rating = db.query(models.Rating).filter(models.Rating.id == rating_id).first()
    if rating is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found"
        )
    
    # Only allow users to delete their own ratings or admins to delete any rating
    if rating.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db.delete(rating)
    db.commit()
    return None 
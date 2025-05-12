from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Rating, User
from schemas import RatingCreate, RatingResponse, TokenData
from .auth import oauth2_scheme, SECRET_KEY, ALGORITHM
from jose import jwt, JWTError

router = APIRouter(
    prefix="/ratings",
    tags=["ratings"]
)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user

@router.post("/", response_model=RatingResponse)
def create_rating(
    rating: RatingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_rating = Rating(
        rating=rating.rating,
        comment=rating.comment,
        user_id=current_user.id
    )
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    return db_rating

@router.get("/", response_model=List[RatingResponse])
def get_ratings(db: Session = Depends(get_db)):
    ratings = db.query(Rating).all()
    return ratings 
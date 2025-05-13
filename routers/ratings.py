from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Rating, User
from schemas import RatingCreate, RatingResponse, TokenData
from .auth import oauth2_scheme
from jose import jwt, JWTError
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get security configuration from environment
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

router = APIRouter(
    prefix="/ratings",
    tags=["ratings"]
)

@router.options("/")
async def options_ratings():
    return Response(status_code=200)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        print(f"Received token: {token}")  # Debug log
        print(f"Using SECRET_KEY: {SECRET_KEY}")  # Debug log
        print(f"Using ALGORITHM: {ALGORITHM}")  # Debug log
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Decoded payload: {payload}")  # Debug log
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError as e:
        print(f"JWT Error: {str(e)}")  # Debug log
        raise credentials_exception
    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        print(f"User not found for email: {email}")  # Debug log
        raise credentials_exception
    return user

@router.post("/", response_model=RatingResponse)
def create_rating(rating: RatingCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_rating = Rating(
        user_id=current_user.id,
        rating=rating.rating,
        comment=rating.comment
    )
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    return RatingResponse.from_orm(db_rating)

@router.get("/", response_model=List[RatingResponse])
def get_ratings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    ratings = db.query(Rating).offset(skip).limit(limit).all()
    return [RatingResponse.from_orm(rating) for rating in ratings] 
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import users, auth, ratings
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://sawyeranderson.github.io",  # Add your GitHub Pages domain
    "https://*.github.io",  # Allow all GitHub Pages subdomains
    "https://sawyeranderson.net",
    "https://www.sawyeranderson.net",
    "https://sawyeranderson-backend.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Include routers
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(ratings.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the API"} 
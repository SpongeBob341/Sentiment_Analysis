from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import os

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/mydatabase")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define the Message model
class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)

# Define the RedditPost model
class RedditPost(Base):
    __tablename__ = "reddit_posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    sentiment = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create database tables
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root(db: Session = Depends(get_db)):
    # Save a test message
    test_message = Message(text="Hello from FastAPI and PostgreSQL!")
    db.add(test_message)
    db.commit()
    db.refresh(test_message)

    # Retrieve all messages
    messages = db.query(Message).all()
    return {"message": "Test message saved and retrieved!", "all_messages": [{"id": msg.id, "text": msg.text} for msg in messages]}

@app.get("/reddit-sentiment")
def get_reddit_sentiment(db: Session = Depends(get_db)):
    posts = db.query(RedditPost).all()
    return [{"id": post.id, "title": post.title, "sentiment": post.sentiment, "created_at": post.created_at.isoformat()} for post in posts]





import os
import praw
from transformers import pipeline
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Reddit API credentials 
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")
REDDIT_USER = os.getenv("REDDIT_USER")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")

# Initialize Reddit API
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT,
    username=REDDIT_USER,
    password=REDDIT_PASSWORD
)

# Initialize sentiment analysis pipeline
sentiment_pipeline = pipeline("sentiment-analysis")

# Database setup 
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/mydatabase")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class RedditPost(Base):
    __tablename__ = "reddit_posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    sentiment = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def collect_and_analyze_reddit_posts(subreddit_name="all", limit=10):
    """
    Tests the Reddit API connection, then collects and analyzes posts,
    saving them to the database.
    """
    print("Connecting to database...")
    db = next(get_db()) # Get a database session

    try:
        # 1. Test the Reddit API connection first
        print("Testing Reddit API connection...")
        user = reddit.user.me()
        if not user:
            # This handles a case where login succeeds but no user is returned
            raise Exception("Could not retrieve Reddit user info. Check credentials.")
        
        print(f"Successfully connected to Reddit as: {user.name}")

        # 2. Proceed with collection if API test is successful
        print(f"Collecting {limit} posts from r/{subreddit_name}...")
        
        # Ensure tables are created if this script is run independently
        Base.metadata.create_all(bind=engine)

        for submission in reddit.subreddit(subreddit_name).hot(limit=limit):
            title = submission.title
            sentiment_result = sentiment_pipeline(title)[0]
            sentiment_label = sentiment_result['label']

            print(f"Post: '{title}' | Sentiment: {sentiment_label}")

            # Save to database
            reddit_post = RedditPost(
                title=title,
                sentiment=sentiment_label,
                created_at=datetime.fromtimestamp(submission.created_utc)
            )
            db.add(reddit_post)
        
        db.commit()
        print("Successfully collected and analyzed posts, and saved to database.")

    except Exception as e:
        print(f"An error occurred: {e}")
        # Rollback any changes if an error occurred during API check or collection
        db.rollback() 
    finally:
        print("Closing database session.")
        db.close()

if __name__ == "__main__":
    collect_and_analyze_reddit_posts()


# TESTER
'''
import praw

reddit = praw.Reddit(
    client_id="tf6m0cZkN9-cE6pMCD0eWg",
    client_secret="o3dJrfWk6KagD2LHfJHuctXb2qixVQ",
    user_agent="SpongeBob:v1.0 (by /u/Sponge_Bob1662)",
    username="Sponge_Bob1662",
    password="Happy@15092003"
)

# This will test your login
print(reddit.user.me())
'''

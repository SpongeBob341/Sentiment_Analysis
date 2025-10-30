import os
import praw
from transformers import pipeline
import yaml

def load_reddit_credentials_from_docker_compose():
    compose_path = os.path.join(os.path.dirname(__file__), "..", "docker-compose.yml")
    with open(compose_path, 'r') as f:
        compose_config = yaml.safe_load(f)
    
    environment = compose_config['services']['collector']['environment']
    
    credentials = {}
    for item in environment:
        if '=' in item:
            key, value = item.split('=', 1)
            credentials[key.strip()] = value.strip().strip('"')
            
    return credentials

reddit_credentials = load_reddit_credentials_from_docker_compose()

# Reddit API credentials 
REDDIT_CLIENT_ID = reddit_credentials.get("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = reddit_credentials.get("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = reddit_credentials.get("REDDIT_USER_AGENT")
REDDIT_PASSWORD = reddit_credentials.get("REDDIT_PASSWORD")


# Initialize Reddit API
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT,
    username=REDDIT_USER_AGENT,
    password=REDDIT_PASSWORD
)

# Initialize sentiment analysis pipeline
sentiment_pipeline = pipeline("sentiment-analysis")

def collect_and_analyze_reddit_posts(subreddit_name="all", limit=10):
    print(f"Collecting {limit} posts from r/{subreddit_name}...")

    try:
        for submission in reddit.subreddit(subreddit_name).hot(limit=limit):
            title = submission.title
            sentiment_result = sentiment_pipeline(title)[0]
            sentiment_label = sentiment_result['label']

            print(f"Post: '{title}' | Sentiment: {sentiment_label}")

        print("Successfully collected and analyzed posts.")
    except Exception as e:
        print(f"An error occurred: {e}")

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

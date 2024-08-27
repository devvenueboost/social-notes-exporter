import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Reddit API credentials
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_REFRESH_TOKEN = os.getenv('REDDIT_REFRESH_TOKEN')
REDDIT_REDIRECT_URI = os.getenv('REDDIT_REDIRECT_URI', 'http://localhost:8080')

# Twitter API credentials
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

# User Agent
USER_AGENT = "python:my_content_exporter:v1.0 (by /u/venueboostdev)"

# Output folder path for Word documents
OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'exported_data')
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Output file path for text export (kept for backwards compatibility)
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'exported_content.txt')
import praw
import traceback
import tweepy
from src.config import (
    REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_REFRESH_TOKEN, USER_AGENT,
    TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET
)


def get_reddit_instance():
    try:
        print(f"Attempting to create Reddit instance...")
        print(f"Client ID: {REDDIT_CLIENT_ID[:5]}...")
        print(f"Client Secret: {REDDIT_CLIENT_SECRET[:5]}...")
        print(f"Refresh Token: {REDDIT_REFRESH_TOKEN[:5]}...")
        print(f"User Agent: {USER_AGENT}")

        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            refresh_token=REDDIT_REFRESH_TOKEN,
            user_agent=USER_AGENT,
            scope="identity history read save"
        )

        print("Reddit instance created. Attempting to get user information...")
        user = reddit.user.me()
        if user is None:
            print("Failed to get user information. User is None.")
            return None
        print(f"Successfully authenticated as user: {user.name}")

        return reddit
    except Exception as e:
        print(f"Error in get_reddit_instance: {str(e)}")
        print(traceback.format_exc())
        return None



def get_twitter_api():
    auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
    auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
    return tweepy.API(auth)
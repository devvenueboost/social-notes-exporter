import os
import requests
from dotenv import load_dotenv
import praw
import random
import string
import webbrowser
import tweepy
from flask import Flask, request
import requests
from src.config import (
    REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_REFRESH_TOKEN, USER_AGENT,
    TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET
)


def refresh_token_if_needed():
    load_dotenv()  # Reload environment variables
    refresh_token = os.getenv('REDDIT_REFRESH_TOKEN')

    if not refresh_token:
        print("No refresh token found. Initiating new token generation.")
        return get_new_token()

    # Check if the current token is valid
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        refresh_token=refresh_token,
        user_agent=USER_AGENT
    )

    try:
        reddit.user.me()
        print("Existing token is valid.")
        return refresh_token
    except:
        print("Existing token is invalid. Refreshing token.")
        return get_new_token()


def get_new_token():
    # This function will use the logic from get_reddit_token.py
    # For brevity, I'm not including the full implementation here
    # You should move the token generation logic from get_reddit_token.py to this function
    new_token = generate_new_token()  # Implement this function based on get_reddit_token.py

    # Update .env file with new token
    with open('.env', 'r') as file:
        lines = file.readlines()
    with open('.env', 'w') as file:
        for line in lines:
            if line.startswith('REDDIT_REFRESH_TOKEN='):
                file.write(f'REDDIT_REFRESH_TOKEN={new_token}\n')
            else:
                file.write(line)

    return new_token

def get_reddit_instance():
    refresh_token = refresh_token_if_needed()
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        refresh_token=refresh_token,
        user_agent=USER_AGENT
    )
    return reddit


def generate_new_token():
    app = Flask(__name__)

    @app.route('/callback')
    def callback():
        error = request.args.get('error', '')
        if error:
            return f"Error: {error}"
        code = request.args.get('code')

        # Exchange code for token
        token_url = "https://www.reddit.com/api/v1/access_token"
        client_auth = requests.auth.HTTPBasicAuth(REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET)
        post_data = {"grant_type": "authorization_code", "code": code, "redirect_uri": "http://localhost:8000/callback"}
        headers = {"User-Agent": USER_AGENT}
        response = requests.post(token_url, auth=client_auth, data=post_data, headers=headers)
        token_data = response.json()

        return token_data.get('refresh_token')

    # Generate random state
    state = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))

    # Construct the auth URL
    auth_url = f"https://www.reddit.com/api/v1/authorize?client_id={REDDIT_CLIENT_ID}&response_type=code&state={state}&redirect_uri=http://localhost:8000/callback&duration=permanent&scope=identity history read save"

    # Open browser for user to authenticate
    webbrowser.open_new(auth_url)

    # Run Flask app to handle callback
    return app.run(port=8000)

def get_twitter_api():
    auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
    auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
    return tweepy.API(auth)
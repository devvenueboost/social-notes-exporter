import random
import string
import webbrowser
from flask import Flask, request
from src.config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, USER_AGENT
import requests

app = Flask(__name__)

REDIRECT_URI = "http://localhost:8000/callback"
SCOPES = "identity history read save"

@app.route('/')
def homepage():
    return "The authentication flow has completed. You may close this tab."

@app.route('/callback')
def callback():
    error = request.args.get('error', '')
    if error:
        return f"Error: {error}"
    state = request.args.get('state', '')
    if state != app.config['STATE']:
        return "Error: State mismatch"
    code = request.args.get('code')
    token_url = "https://www.reddit.com/api/v1/access_token"
    client_auth = requests.auth.HTTPBasicAuth(REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET)
    post_data = {"grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECT_URI}
    headers = {"User-Agent": USER_AGENT}
    response = requests.post(token_url, auth=client_auth, data=post_data, headers=headers)
    token_data = response.json()
    refresh_token = token_data.get('refresh_token')
    if refresh_token:
        print(f"\nYour refresh token is: {refresh_token}")
        print("Add this to your .env file as REDDIT_REFRESH_TOKEN")
    else:
        print(f"Error getting refresh token. Response: {token_data}")
    return "The authentication flow has completed. You may close this tab."

def main():
    state = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))
    app.config['STATE'] = state
    auth_url = f"https://www.reddit.com/api/v1/authorize?client_id={REDDIT_CLIENT_ID}&response_type=code&state={state}&redirect_uri={REDIRECT_URI}&duration=permanent&scope={SCOPES}"
    print(f"Opening browser to: {auth_url}")
    webbrowser.open_new(auth_url)
    app.run(port=8000)

if __name__ == "__main__":
    main()
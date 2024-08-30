from flask import Flask, jsonify, send_file, request
from src.exporter import reddit_api, twitter_api
from src.auth import get_reddit_instance
from src.auth import refresh_token_if_needed
import traceback
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/reddit/export', methods=['GET'])
def reddit_export():
    try:
        refresh_token_if_needed()
        filename = reddit_api()
        if filename:
            return send_file(filename, as_attachment=True)
        else:
            return jsonify({"error": "No content found to export"}), 404
    except Exception as e:
        error_message = f"An error occurred: {str(e)}\n{traceback.format_exc()}"
        print(error_message)
        return jsonify({"error": error_message}), 500

@app.route('/twitter/export/<username>', methods=['GET'])
def twitter_export(username):
    filename = twitter_api(username)
    if filename:
        return send_file(filename, as_attachment=True)
    else:
        return jsonify({"error": "Failed to create document"}), 400

@app.route('/test_reddit', methods=['GET'])
def test_reddit():
    try:
        reddit = get_reddit_instance()
        if reddit is None:
            return jsonify({
                "status": "error",
                "message": "Failed to create Reddit instance"
            }), 500

        user = reddit.user.me()
        if user is None:
            return jsonify({
                "status": "error",
                "message": "Failed to get user information"
            }), 500

        saved_count = len(list(user.saved(limit=None)))
        return jsonify({
            "status": "success",
            "username": user.name,
            "saved_items_count": saved_count
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }), 500

def crawl_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract title
    title = soup.title.string if soup.title else "No title found"
    
    # Extract all links
    links = [a['href'] for a in soup.find_all('a', href=True)]
    
    # Extract all text
    text = soup.get_text()
    
    return {
        "title": title,
        "links": links,
        "text": text
    }

@app.route('/crawl', methods=['POST'])
def crawl_website():
    try:
        data = request.json
        url = data.get('url')
        
        if not url:
            return jsonify({"error": "URL is required"}), 400

        result = crawl_url(url)

        return jsonify({
            "status": "success",
            "data": result
        })
    except Exception as e:
        error_message = f"An error occurred: {str(e)}\n{traceback.format_exc()}"
        print(error_message)
        return jsonify({"error": error_message}), 500

if __name__ == '__main__':
    app.run(debug=True)
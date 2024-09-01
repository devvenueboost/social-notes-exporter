from flask import Flask, jsonify, send_file, request
from src.exporter import reddit_api, twitter_api
from src.auth import get_reddit_instance
from src.auth import refresh_token_if_needed
import traceback
import requests
from bs4 import BeautifulSoup
from src.models.models import SessionLocal, Post
import uuid
from datetime import datetime
import ast
import html

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
    
    title = soup.title.string if soup.title else "No title found"
    links = [a['href'] for a in soup.find_all('a', href=True)]
    text = soup.get_text()
    categories = [meta['content'] for meta in soup.find_all('meta', {'name': 'category'})]
    published_time = soup.find('time')['datetime'] if soup.find('time') else "No published time found"
    
    posts = []
    for article in soup.find_all('article', class_='jeg_post'):
        post_title = article.find('h3', class_='jeg_post_title')
        post_title = post_title.get_text() if post_title else "No title"
        
        post_content_link = article.find('a', href=True)
        post_content_link = post_content_link['href'] if post_content_link else "No link"
        
        post_date = article.find('div', class_='jeg_meta_date')
        post_date = post_date.get_text().strip() if post_date else "No date"
        
        post_categories = [cat.get_text() for cat in article.find_all('a', class_='category-aktualitet')]
        
        posts.append({
            "title": post_title,
            "content_link": post_content_link,
            "date": post_date,
            "categories": post_categories
        })
    
    return {
        "title": title,
        "links": links,
        "text": text,
        "categories": categories,
        "published_time": published_time,
        "posts": posts
    }

@app.route('/crawl', methods=['POST'])
def crawl_website():
    try:
        data = request.json
        url = data.get('url')
        
        if not url:
            return jsonify({"error": "URL is required"}), 400

        result = crawl_url(url)
        
        db = SessionLocal()
        for post_data in result['posts']:
            post = Post(
                id=str(uuid.uuid4()),
                title=post_data['title'],
                links=post_data['content_link'],
                text="",
                categories=str(post_data['categories']),
                published_time=datetime.strptime(post_data['date'].strip(), '%H:%M %d/%m/%Y') if post_data['date'] != "No date" else None
            )
            db.add(post)
        db.commit()
        db.close()

        return jsonify({
            "status": "success",
            "data": result
        })
    except Exception as e:
        error_message = f"An error occurred: {str(e)}\n{traceback.format_exc()}"
        print(error_message)
        return jsonify({"error": error_message}), 500

@app.route('/posts', methods=['GET'])
def get_posts():
    try:
        db = SessionLocal()
        posts = db.query(Post).all()
        db.close()
        
        posts_data = [{
            "id": post.id,
            "title": post.title.strip() if post.title else "",
            "text": html.escape(post.text.strip().replace('\n', ' ')) if post.text else "",
            "categories": ast.literal_eval(post.categories) if post.categories else [],
            "published_time": post.published_time
        } for post in posts if post.title]

        return jsonify({
            "status": "success",
            "data": posts_data
        })
    except Exception as e:
        error_message = f"An error occurred: {str(e)}\n{traceback.format_exc()}"
        print(error_message)
        return jsonify({"error": error_message}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
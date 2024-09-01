from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from markupsafe import Markup  # Change this line
from src import db, init_app
from src.models.models import RedditPost, RedditComment
from src.exporter import reddit_api
import os
from dotenv import load_dotenv, set_key, find_dotenv
import markdown2
import re

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app_data.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    init_app(app)

    with app.app_context():
        db.create_all()

    @app.route('/dashboard', methods=['GET', 'POST'])
    def dashboard():
        dotenv_path = find_dotenv()
        load_dotenv(dotenv_path)

        if request.method == 'POST':
            client_id = request.form.get('client_id')
            client_secret = request.form.get('client_secret')
            
            set_key(dotenv_path, 'REDDIT_CLIENT_ID', client_id)
            set_key(dotenv_path, 'REDDIT_CLIENT_SECRET', client_secret)
            
            load_dotenv(dotenv_path, override=True)
            
            return redirect(url_for('dashboard'))

        client_id = os.getenv('REDDIT_CLIENT_ID', '')
        client_secret = os.getenv('REDDIT_CLIENT_SECRET', '')

        reddit_post_count = RedditPost.query.count()
        reddit_comment_count = RedditComment.query.count()
        
        return render_template('dashboard.html', client_id=client_id, client_secret=client_secret, 
                               reddit_post_count=reddit_post_count, reddit_comment_count=reddit_comment_count)

    @app.route('/call_reddit_export', methods=['GET'])
    def call_reddit_export():
        try:
            filename = reddit_api()
            
            if filename and os.path.exists(filename):
                return send_file(filename, as_attachment=True, download_name='reddit_posts.docx', 
                                 mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            else:
                return jsonify({"error": "Failed to generate export file"}), 500
        except Exception as e:
            print(f"Error in call_reddit_export: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route('/posts')
    def list_posts():
        page = request.args.get('page', 1, type=int)
        per_page = 10  # Number of posts per page
        posts = RedditPost.query.order_by(RedditPost.created_utc.desc()).paginate(page=page, per_page=per_page, error_out=False)
        
        # Prepare comments for each post
        for post in posts.items:
            post.paginated_comments = RedditComment.query.filter_by(post_id=post.id).order_by(RedditComment.created_utc.desc()).paginate(page=1, per_page=5, error_out=False)
        
        return render_template('posts.html', posts=posts)

    @app.route('/post/<string:post_id>/comments')
    def post_comments(post_id):
        post = RedditPost.query.get_or_404(post_id)
        page = request.args.get('page', 1, type=int)
        per_page = 5  # Number of comments per page
        comments = RedditComment.query.filter_by(post_id=post_id).order_by(RedditComment.created_utc.desc()).paginate(page=page, per_page=per_page, error_out=False)
        return render_template('comments_partial.html', post=post, comments=comments)

    def markdown_to_html(text):
        # Convert Reddit-style links to markdown links
        text = re.sub(r'@(https?://(?:www\.)?reddit\.com/\S+)', r'[\1](\1)', text)
        
        # Convert plain URLs to markdown links
        text = re.sub(r'(https?://(?:www\.)?reddit\.com/\S+)', r'[\1](\1)', text)
        
        # Define link patterns
        link_patterns = [
            (re.compile(r'(https?://(?:www\.)?reddit\.com/\S+)'), r'\1'),
        ]
        
        # Use markdown2 with extras for better link parsing
        html = markdown2.markdown(text, extras={
            "link-patterns": link_patterns,
            "cuddled-lists": None,
            "code-friendly": None,
        })
        
        return Markup(html)

    app.jinja_env.filters['markdown'] = markdown_to_html

    return app

# If you have any other routes or functions, include them here
from src import db
from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class RedditPost(db.Model):
    __tablename__ = 'reddit_posts'
    id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String)
    url = db.Column(db.String)
    selftext = db.Column(db.Text)
    subreddit = db.Column(db.String)
    created_utc = db.Column(db.DateTime, index=True)
    comments = db.relationship('RedditComment', back_populates='post', cascade='all, delete-orphan')

class RedditComment(db.Model):
    __tablename__ = 'reddit_comments'
    id = db.Column(db.String, primary_key=True)
    post_id = db.Column(db.String, db.ForeignKey('reddit_posts.id'), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String)
    created_utc = db.Column(db.DateTime)
    post = db.relationship('RedditPost', back_populates='comments')


class Post(Base):
    __tablename__ = 'posts'
    id = Column(String, primary_key=True)
    title = Column(String)
    links = Column(Text)
    text = Column(Text)
    categories = Column(Text)
    published_time = Column(DateTime)

DATABASE_URL = "sqlite:///scraped_data.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, BLOB, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, backref
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer,  primary_key = True, nullable = False)
    email = Column(String, nullable=False, unique = True)
    username = Column(String, nullable=False, unique = True)
    role = Column(String, nullable=False)
    # password = Column(String, nullable=False)
    profile_pic = Column(BLOB, nullable=False)
    mimetype = Column(String, nullable=False)
    status = Column(Boolean, nullable=False)
    created_at = Column(DateTime, server_default = func.now(), nullable=False)
    updated_at = Column(DateTime, server_default = func.now(), server_onupdate = func.now(), nullable=False)
    password_hash = Column(String, nullable = False)

    # Some Password Stuff
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # can have many posts
    poster = db.relationship('Posts', backref=backref('poster'), cascade = 'all, delete')
    reporter = db.relationship('Reports', backref=backref('reporter'), cascade = 'all, delete')
    bookmarker = db.relationship('Bookmarks', backref=backref('bookmarker'), cascade = 'all, delete')
    notifier = db.relationship('Notifications', backref=backref('notifier'), cascade = 'all, delete')


class Posts(db.Model):
    id = Column(Integer, primary_key = True)
    poster_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    type_id = Column(Integer, ForeignKey('types.id'), nullable=False)
    description = Column(String, nullable=False)
    created_at = Column(DateTime, server_default = func.now(), nullable=False)
    updated_at = Column(DateTime, server_default = func.now(), server_onupdate = func.now(), nullable=False)
    
    article = db.relationship('News', backref=backref('article'), cascade = 'all, delete')
    post = db.relationship('Reports', backref=backref('post'), cascade = 'all, delete')
    comment_post = db.relationship('Comments', backref=backref('comment_post'), cascade = 'all, delete')

class News(db.Model):
    id = Column(Integer, primary_key = True)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    title = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    image = Column(BLOB, nullable=False)
    mimetype = Column(String, nullable=False)
    views = Column(Integer, nullable=False)
    published = Column(Boolean, nullable = False)
    
    commented_news = db.relationship('Comments', backref = backref('commented_news'), cascade = 'all, delete')

class Comments(db.Model):
    id = Column(Integer, primary_key = True)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable = False)
    news_id = Column(Integer, ForeignKey('news.id'), nullable = False)
    is_reply = Column(Boolean, nullable = False)

class Types(db.Model):
    id = Column(Integer, primary_key = True)
    name = Column(String, nullable=False)
    type = db.relationship('Posts', backref=backref('type'), cascade = 'all, delete')

class Categories(db.Model):
    id = Column(Integer, primary_key = True)
    name = Column(String, nullable=False)
    category = db.relationship('News', backref=backref('category'), cascade = 'all, delete')


class Roles(db.Model):
    id = Column(Integer, primary_key = True)
    name = Column(String, nullable=False)


class Followers(db.Model):
    id = Column(Integer, primary_key = True)
    follow_by = Column(Integer, nullable=False)
    follow_to = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default = func.now(), nullable=False)


class Reports(db.Model):
    id = Column(Integer, primary_key = True)
    reporter_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    reason = Column(String, nullable=True)
    created_at = Column(DateTime, server_default = func.now(), nullable=False)

class Bookmarks(db.Model):
    id = Column(Integer, primary_key = True)
    bookmarker_id = Column(Integer, ForeignKey('users.id'), nullable = False)
    news_id = Column(Integer, ForeignKey('news.id'), nullable = False)
    news = db.relationship('News', backref=db.backref('news'))

class Notifications(db.Model):
    id = Column(Integer, primary_key = True)
    notifier_id = Column(Integer, ForeignKey('users.id'), nullable = False)
    activity = Column(String, nullable = False)
    link = Column(String, nullable = True)
    created_at = Column(DateTime, server_default = func.now(), nullable=False)

class History(db.Model):
    id = Column(Integer, primary_key = True)
    news_id = Column(Integer, ForeignKey('news.id'), nullable = False)
    created_at = Column(DateTime, server_default = func.now(), nullable=False)

class Analytics(db.Model):
    __tablename__ = "analytics"

    index = db.Column(db.Integer, primary_key=True, autoincrement=True)
    response_time = db.Column(db.Float)
    date = db.Column(db.DateTime)
    method = db.Column(db.String)
    size = db.Column(db.Integer)
    status_code = db.Column(db.Integer)
    path = db.Column(db.String)
    user_agent = db.Column(db.String)
    remote_address = db.Column(db.String)
    exception = db.Column(db.String)
    referrer = db.Column(db.String)
    browser = db.Column(db.String)
    platform = db.Column(db.String)
    mimetype = db.Column(db.String)
    

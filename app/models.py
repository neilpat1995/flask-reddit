from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    threads = db.relationship('Thread', backref='user', lazy='dynamic')
    comments = db.relationship('Comment', backref='user', lazy='dynamic')    

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, text_password):
        self.password_hash = generate_password_hash(text_password)

    def check_password(self, text_password):
        return check_password_hash(self.password_hash, text_password)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Thread(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), index=True, unique=True)
    body = db.Column(db.String(256))
    date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    upvotes = db.Column(db.Integer)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    subreddit_id = db.Column(db.Integer, db.ForeignKey('subreddit.id'))

    def __repr__(self):
        return '<Thread {}>'.format(self.title) 

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(256))
    date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    upvotes = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) 
    thread_id = db.Column(db.Integer, db.ForeignKey('thread.id'))

    def __repr__(self):
        return '<Comment {}>'.format(self.body) 

class Subreddit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)

    def __repr__(self):
        return '<Subreddit {}>'.format(self.name)

from flask_login import UserMixin
from config import db
from datetime import datetime


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(64), unique=True)
    name = db.Column(db.String(16))
    password = db.Column(db.String(32))
    sex = db.Column(db.String(16), default='保密')
    avatar = db.Column(db.String(64),default='/static/timg.jpg')
    article = db.relationship('Article', backref='owner_user', cascade='all, delete-orphan', passive_deletes=True)
    comment = db.relationship('Comment', backref='owner_user', cascade='all, delete-orphan', passive_deletes=True)
    reply = db.relationship('Reply', backref='owner_user', cascade='all, delete-orphan', passive_deletes=True)
    thumb_list = db.relationship('Thumb', backref='owner_user', cascade='all, delete-orphan'
                                 , passive_deletes=True)
    collection_list = db.relationship('Collection', backref='owner_user', cascade='all, delete-orphan'
                                      , passive_deletes=True)

    def __repr__(self):
        return '<User %r>' % self.id


class Article(db.Model):
    __tablename__ = 'article'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(32))
    image = db.Column(db.Text)
    text = db.Column(db.Text)
    position = db.Column(db.String(64))
    start = db.Column(db.String(32))
    days = db.Column(db.String(16))
    people = db.Column(db.String(32))
    pay = db.Column(db.String(32))
    thumb = db.Column(db.Integer)
    collection = db.Column(db.Integer)
    comment = db.relationship('Comment', backref='owner_article', cascade='all, delete-orphan', passive_deletes=True)
    thumb_list = db.relationship('Thumb', backref='owner_article', cascade='all, delete-orphan', passive_deletes=True)
    collection_list = db.relationship('Collection', backref='owner_article', cascade='all, delete-orphan'
                                      , passive_deletes=True)
    article_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    time = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<Article %r>' % self.id


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reply = db.relationship('Reply', backref='owner_comment', cascade='all, delete-orphan', passive_deletes=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    article_id = db.Column(db.Integer, db.ForeignKey('article.id', ondelete='CASCADE'))
    comment = db.Column(db.Text)
    time = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<Comment %r>' % self.id


class Reply(db.Model):
    __tablename__ = 'replies'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reply = db.Column(db.Text)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    time = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<Reply %r>' % self.id


class Thumb(db.Model):
    __tablename__ = 'thumb'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    article_id = db.Column(db.Integer, db.ForeignKey('article.id', ondelete='CASCADE'))

    def __repr__(self):
        return '<Thumb %r>' % self.id

class Collection(db.Model):
    __tablename__ = 'collection'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    articleid = db.Column(db.Integer, db.ForeignKey('article.id', ondelete='CASCADE'))

    def __repr__(self):
        return '<Collection %r>' % self.id
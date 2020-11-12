from datetime import datetime
from twitter_clone import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    tweets = db.relationship('Tweet', backref='author', lazy=True)

    def get_id(self):
           return (self.user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Tweet(db.Model):
    tweet_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False) #check foreign key
    date_tweeted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    tweet = db.Column(db.String(140), nullable=False)
    
    def get_id(self):
           return (self.tweet_id)

    def __repr__(self):
        return f"Tweet('{self.tweet}', '{self.date_tweeted}')"


class Followers(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    following = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)

    def get_id(self):
           return (self.user_id)
           
    def __repr__(self):
        pass


#https://stackoverflow.com/questions/7150306/help-with-a-microblog-twitter-clone-database-structure
'''
CREATE TABLE followers (
  id_user INT NOT NULL REFERENCES users (user_id),
  id_following INT NOT NULL REFERENCES users (user_id),
  PRIMARY KEY (id_user, id_following)
) 
'''
'''
CREATE TABLE tweets (
  tweet_id INT NOT NULL AUTO_INCREMENT,
  user_id INT NOT NULL
  tweet VARCHAR(140) NOT NULL,
  PRIMARY KEY (tweet_id),
  FOREIGN KEY user_id(user_id) REFERENCES users(user_id) 
  ON UPDATE CASCADE ON DELETE CASCADE
) 
'''
'''
CREATE TABLE users (
  user_id INT NOT NULL AUTO_INCREMENT,
  user VARCHAR(255) NOT NULL,
  /*password VARCHAR(40) NOT NULL,*/<<--- NEVER STORE A PASSWORD IN THE CLEAR!
  passhash VARCHAR(40) NOT NULL,
  email VARCHAR(255) NOT NULL,
  PRIMARY KEY (user_id)
) 
'''
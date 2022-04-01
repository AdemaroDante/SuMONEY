'''
Models of tables in database. 
'''
from db import db
import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Articles(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable = False)
    subtitle = db.Column(db.String(65), nullable = False)
    type = db.Column(db.String())
    content = db.Column(db.Text())
    added_by = db.Column(db.String(35), nullable = False)
    date = db.Column(db.DateTime, default=datetime.datetime.now())

    # Create a string
    def __repr__(self):
        return '<Name %r>' % self.name

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(35), nullable = False)
    firstname = db.Column(db.String(100), nullable = False)
    lastname = db.Column(db.String(100), nullable = False)
    description = db.Column(db.String(1000), nullable = True)
    mail = db.Column(db.String(100), nullable = False, unique = True) # Mail verification in BETA ver.
    password_hash = db.Column(db.String(128), nullable = False)

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

class Messages(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    sender = db.Column(db.String(50), nullable = False)
    sender_mail = db.Column(db.String(80), nullable = False)
    recipient = db.Column(db.String(50), nullable = False)
    subject = db.Column(db.String(50), nullable = True)
    content = db.Column(db.String(50), nullable = True)
    date = db.Column(db.DateTime, default=datetime.datetime.now())
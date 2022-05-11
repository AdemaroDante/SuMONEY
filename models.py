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
    img = db.Column(db.String())
    date = db.Column(db.DateTime)

    # Create a string
    def __repr__(self):
        return '<Name %r>' % self.name

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    firstname = db.Column(db.String(100), nullable = False)
    lastname = db.Column(db.String(100), nullable = False)
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

class Members(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable = False)
    description = db.Column(db.String(500), nullable = True)
    img = db.Column(db.String())
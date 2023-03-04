from project_files import db

from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    first_name = db.Column(db.String(30),unique=False, nullable=False)
    surname = db.Column(db.String(30), unique=False, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), unique=False, nullable=False)
    ip = db.Column(db.String(20), unique=False, nullable=False)
    account_type = db.Column(db.String(30), unique=False, nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    points = db.Column(db.Integer, default=0)
    newsletter = db.Column(db.Boolean, nullable=False)
    date = db.Column(db.String(30), unique=False, nullable=False)


    def __repr__(self):
        return f'User {self.username}'


class Blocked(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=False, nullable=False)
    ip = db.Column(db.String(30), unique=False, nullable=False)
    date = db.Column(db.String(30), unique=False, nullable=False)

    def __repr__(self):
        return f'Blocked {self.username}'
    

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=False, nullable=False)
    category = db.Column(db.String(30), unique=False, nullable=False)
    company = db.Column(db.String(30), unique=False, nullable=False)
    price = db.Column(db.Integer(), unique=False, nullable=False)
    date = db.Column(db.String(30), unique=False, nullable=False)


    def __repr__(self):
        return f'Product {self.name}'
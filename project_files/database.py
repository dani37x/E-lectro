from project_files import db

from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    first_name = db.Column(db.String(30),unique=False, nullable=False)
    surname = db.Column(db.String(30), unique=False, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(20), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

    # def is_active(self):
    #     return True

    # def get_id(self):
    #     return self.email

    def is_authenticated(self):
        return self.authenticated

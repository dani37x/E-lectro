from project_files import db
from project_files import bcrypt

from flask_login import UserMixin

from datetime import datetime


class Base():

    @property
    def all_rows(self):
        return self.query.all()
    
    
    @staticmethod
    def password_hash(password):
        return bcrypt.generate_password_hash(password).decode('utf-8')

    
    def get_by_row_id(self, value):
        return self.query.get(int(value))


    def show_row(self, column, value):
        filter_condition = {column: value}
        return self.query.filter_by(**filter_condition).first()


    def add_row_to_db(self):
        db.session.add(self)
        db.session.commit()


    def update_row(self, **kwargs):
        for key, value in kwargs.items():
            if value == '' or value == None:
                return ValueError('Field can not be empty')
            if value == 'False' or value == 'True':
                value = True if 'True' in value else False
            if key == 'password':
                value = self.password_hash(value)
            setattr(self, key, value)
        db.session.commit()
    

    def delete_row(self):
        db.session.delete(self)
        db.session.commit()



class Users(db.Model, UserMixin, Base):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    first_name = db.Column(db.String(30),unique=False, nullable=False)
    surname = db.Column(db.String(30), unique=False, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), unique=False, nullable=False)
    ip = db.Column(db.String(20), unique=False, nullable=False)
    account_type = db.Column(db.String(30), unique=False, nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    points = db.Column(db.Integer, default=0)
    newsletter = db.Column(db.Boolean, nullable=False)
    date = db.Column(
        db.String(30),
        unique=False, 
        nullable=False, 
        default=datetime.now().strftime('%d-%m-%Y  %H:%M:%S')
    )
    product = db.relationship(
        'UsersProducts', 
        backref=db.backref('users', lazy=True)
    )


    def __repr__(self):
        return f'Users(id={self.id}, username={self.username})'
        


class BlockedUsers(Base, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=False, nullable=False)
    ip = db.Column(db.String(30), unique=False, nullable=False)
    date = db.Column(
        db.String(30), 
        unique=False, 
        nullable=False, 
        default=datetime.now().strftime('%d-%m-%Y  %H:%M:%S')
    )


    def __repr__(self):
        return f'BlockedUsers(id={self.id}, username={self.username})'
    
    


class Products(Base, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=False, nullable=False)
    category = db.Column(db.String(30), unique=False, nullable=False)
    company = db.Column(db.String(30), unique=False, nullable=False)
    price = db.Column(db.Float(), unique=False, nullable=False)
    old_price = db.Column(db.Float(), unique=False, nullable=False)
    date = db.Column(
        db.String(30), 
        unique=False, 
        nullable=False, 
        default=datetime.now().strftime('%d-%m-%Y  %H:%M:%S')
    )
    user = db.relationship(
        'UsersProducts', 
        backref=db.backref('products', lazy=True)
    )


    def __repr__(self):
        return f'Products(id={self.id}, name={self.name})'

    
    

class UsersProducts(Base, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, 
        db.ForeignKey('users.id'), 
        nullable=False
    )
    product_id = db.Column(
        db.Integer, 
        db.ForeignKey('products.id'), 
        nullable=False
    )
    date = db.Column(
        db.String, 
        nullable=False, 
        default=datetime.now().strftime('%d-%m-%Y  %H:%M:%S')
    )
    price = db.Column(db.Float(), unique=False, nullable=False)


    def __repr__(self):
        return f'Column(id={self.id}, user_id={self.user_id}, product_id={self.product_id})'

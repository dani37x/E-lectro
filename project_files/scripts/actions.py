"""
The actions.py file is an essential component of the admin panel. It serves
as the backbone and contains various functions for managing different aspects
of the panel, including Users, Products, and BlockedUsers Users sections.

Some of the functions you can find in this file include managing newsletters,
creating backups and restoring data, managing user accounts and products, and
dealing with blocked users.
"""

from project_files import db
from project_files import app
from project_files import mail
from project_files import queue
from project_files import BLOCKED_USERS, USERS, PRODUCTS, PRICES

from .functions import open_json, save_json , string_to_date
from .functions import save_price, back_to_slash

from ..database import Users, BlockedUsers, Products

from flask_mail import Message

from datetime import datetime, date, timedelta

from rq import Retry

import time

import random


# joint funcs

def delete_rows(model, data):
    time.sleep(10)
    app.app_context().push()


    for number in data:
        model.query.filter_by(id=number).delete()
        db.session.commit()


def backup(model):

    if model == Users:
        path = USERS
    elif model == Products:
        path = PRODUCTS
    else:
        path = BLOCKED_USERS

    data_from_file = open_json(file_path=path)
    objects_list = []
    columns = tuple([m.key for m in model.__table__.columns])
    model_data = model.query.all()

    for row in model_data:
        data = {}
        for column_name in columns:
            data[column_name] = getattr(row, column_name)
        objects_list.append(data)


    if objects_list != data_from_file:
        save_json(file_path=path, data=objects_list)


def restore_database(model):

    if model == Users:
        data_from_file = open_json(file_path=USERS)

        for data in data_from_file:
            user = model(
                username=data['username'],
                first_name=data['first_name'],
                surname=data['surname'],
                email=data['email'],
                password=data['password'],
                ip=data['ip'],
                account_type=data['account_type'],
                active=data['active'],
                points=data['points'],
                newsletter=data['newsletter']
            )
            whether_exist = model.query.filter_by(username=data['username']).first()
            
            if whether_exist == None:
                db.session.add(user)
                db.session.commit()

    elif model == Products:
        data_from_file = open_json(file_path=PRODUCTS)

        for data in data_from_file:
            product = model(
                name=data['name'],
                category=data['category'],
                company=data['company'],
                price=data['price'],
                old_price=data['old_price'],
            )
            whether_exist = model.query.filter_by(name=data['name']).first()

            if whether_exist == None:
                db.session.add(product)
                db.session.commit()

    elif model == BlockedUsers:
        data_from_file = open_json(file_path=BLOCKED_USERS)

        for data in data_from_file:
            blocked = model(
                username=data['username'],
                ip=data['ip'],
                date=data['date'],
            )        
            whether_exist = model.query.filter_by(username=data['username']).first()
            
            if whether_exist == None:
                db.session.add(blocked)
                db.session.commit()


# The funcs of Users panel


def block_users(data):
    time.sleep(5)
    app.app_context().push()

    for id in data:
        user_to_block = Users.query.get(id)
        whether_blocked = BlockedUsers.query.filter_by(username=user_to_block.username).first()

        if whether_blocked == None:
            new_row = BlockedUsers(
                username=user_to_block.username,
                ip=user_to_block.ip,
                date=str((datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y  %H:%M:%S"))
            )
            db.session.add(new_row)
            db.session.commit()


def account_activation(model, data):
    time.sleep(15)
    app.app_context().push()

    for number in data:
        account = model.query.filter_by(id=number).first()
        account.active = True
        db.session.commit()
    

def account_deactivation(model, data):
    time.sleep(15)
    app.app_context().push()

    for number in data:
        account = model.query.filter_by(id=number).first()
        account.active = False
        db.session.commit()


def delete_inactive_accounts():
    time.sleep(60)
    app.app_context().push()
    users = Users.query.all()

    for user in users:
        if user.active ==  False:
            db.session.delete(user)
            db.session.commit()


def message(*args):
    app.app_context().push()  

    if args[0] == 'register':
        subject = 'Register message'
        body = f'Welcome {args[2]}. This is your activation key {args[3]}'

    if args[0] == 'no-reply':
        time.sleep(30)

        subject = 'no-reply-message'
        body = 'Do not reply for this message. This is only test.'

    if args[0] == 'code':
        subject = 'Forgotten password'
        body = f'This is your key {args[3]}'

    if args[0] == 'newsletter':
        subject = 'Special Offer for you'
        a_0 = f'<a href="/shop/products/{args[3][0].id} "> {args[3][0].name} </a> \n'
        a_1 = f'<a href="/shop/products/{args[3][1].id} "> {args[3][1].name} </a> \n'
        a_2 = f'<a href="/shop/products/{args[3][2].id} "> {args[3][2].name} </a> \n'
        a_3 = f'<a href="/shop/products/{args[3][3].id} "> {args[3][3].name} </a> \n'
        a_4 = f'<a href="/shop/products/{args[3][4].id} "> {args[3][4].name} </a> \n\n'
        disclaimer = f'if you do not want receive our the latest products click here \n'
        unsign = f'<a href="/account/newsletter/unregister"> unsign newsletter </a> \n'
        
        body = a_0 + a_1  + a_2 + a_3 + a_4 + disclaimer + unsign
 
    msg = Message(
        subject=subject,
        sender=args[1],
        recipients=args[2]
    )
    msg.body = body
    mail.send(msg)


def send_newsletter():
    time.sleep(15)
    app.app_context().push()

    if users :=  Users.query.filter_by(newsletter=True).all():
        
        if products := Products.query.all():
            products = products[-5:]            
            mails = [user.email for user in users]

            queue.enqueue(
                message, 
                'newsletter', 
                'electro@team.com', 
                mails, 
                products,
                retry=Retry(max=3, interval=[10, 30, 60])
                )



def newsletter_activation(username):
    if user := Users.query.filter_by(username=username).first():      
        user.newsletter = True
        db.session.commit()


def newsletter_deactivation(username):
    if user := Users.query.filter_by(username=username).first():
        user.newsletter = False
        db.session.commit()


# The funcs of Products panel


def discount(percent, data, days=0):
    time.sleep(10)
    app.app_context().push()
    percent = 1-(int(percent)/100)
    
    for product in data:
        product = Products.query.filter_by(id=product).first()
        product.old_price = product.price
        product.price *= percent
        product.price = round(product.price, 2)
        db.session.commit()
        save_price(product=product, days=days)


def price_hike(percent, data, days=0):
    time.sleep(10)
    app.app_context().push()
    percent = 1+(int(percent)/100)

    for product in data:
        product = Products.query.filter_by(id=product).first()
        product.old_price = product.price
        product.price *= percent
        product.price = round(product.price, 2)
        db.session.commit()
        save_price(product=product, days=days)


def previous_price(data):
    app.app_context().push()
    for product in data:
        product = Products.query.filter_by(id=product).first()
        if product.old_price != 0:
            variable = product.price
            product.price = product.old_price
            product.old_price = variable
            db.session.commit()
            save_price(product=product)


def the_price_actions(data, price_type):
    app.app_context().push()
    file_path = back_to_slash(PRICES)
    objects_list = open_json(file_path=file_path)

    for number in data:
        product = Products.query.get(int(number))
        product_info = []
        for obj in objects_list:
            if int(obj['id']) == product.id:
                product_info.append(float(obj['price']))
                product_info.append(float(obj['old_price']))

        variable = product.price

        if price_type == 'the_lowest_price':
            product.price = min(product_info)
            product.old_price = variable

        elif price_type == 'the_highest_price':
            variable = product.price
            product.price = max(product_info)
            product.old_price = variable

        elif price_type == 'the_random_price':
            product.price = random.choice(product_info)
            product.old_price = variable

        save_price(product=product)
        
    db.session.commit()


from project_files import db
from project_files import mail

from .database import User, Blocked, Product

from flask_mail import Message

from datetime import datetime, date, timedelta

import json


def delete_rows(model, data):
    print( model, data)
    for number in data:
        print(model.query.filter_by(id=number))
        model.query.filter_by(id=number).delete()
        db.session.commit()


def block_user(data):
    for id in data:
        user_to_block = User.query.get(id)

        wheter_blocked = Blocked.query.filter_by(username=user_to_block.username).first()
        if wheter_blocked == None:
        
            new_row = Blocked(
                username=user_to_block.username,
                ip=user_to_block.ip,
                date=str((datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y"))
            )
            db.session.add(new_row)
            db.session.commit()


def message(kind, sender, recipents):
    if kind == 'register':
        subject = 'Register message'
        body = f'Welcome {recipents}'

    if kind == 'no-reply':
        subject = 'no-reply-message'
        body = 'Do not reply for this message. This is only test.'

    if kind == 'password':
        user = User.query.filter_by(email=recipents).first()
        subject = 'Password'
        body = f'This is your password {user.password}. Do not show nobody'

    # print(recipents)
    msg = Message(
        subject=subject,
        sender=sender,
        recipients=recipents
    )
    msg.body = body
    mail.send(msg)


def backup(model):

    if model == User:
        path = r'D:\projekty\E-lectro\instance\User.json'
    elif model == Product:
        path = r'D:\projekty\E-lectro\instance\Product.json'
    else:
        path = r'D:\projekty\E-lectro\instance\Blocked.json'


    data_from_file = []
    with open(path) as fp:
        data_from_file = json.load(fp)

    objects_list = []
    columns = tuple([m.key for m in model.__table__.columns])

    model_data = model.query.all()
    for row in model_data:
        data = {}
        for column_name in columns:
            data[column_name] = getattr(row, column_name)
        objects_list.append(data)


    if objects_list != data_from_file:
        with open(path, 'w') as json_file:
            json.dump(objects_list, json_file, indent=4, separators=(',', ': '))
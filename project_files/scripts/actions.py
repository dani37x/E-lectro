from project_files import db
from project_files import mail

from ..database import User, Blocked, Product

from flask_mail import Message

from datetime import datetime, date, timedelta

import json


def delete_rows(model, data):
    print( model, data)
    for number in data:
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


def restore(model):
    pass
    # if model == User:
    #     path = r'D:\projekty\E-lectro\instance\User.json'
    # elif model == Product:
    #     path = r'D:\projekty\E-lectro\instance\Product.json'
    # else:
    #     path = r'D:\projekty\E-lectro\instance\Blocked.json'


    # data_from_file = []
    # with open(path) as fp:
    #     data_from_file = json.load(fp)

    # x = Blocked()
    # db.session.add(x)
    # db.session.commit()

    
    # for data in data_from_file:
    #     values = [value for value in data.values()]
        
    #     values = values[1], values[2], values[3] 
    #     values = list(values)
        # row = Blocked(username=values[0], ip=values[1], date=values[2])
        # db.session.add(row)
        # db.session.commit()


def account_activation(model, data):
    for number in data:
        account = model.query.filter_by(id=number).first()
        account.active = True
        db.session.commit()
    

def account_deactivation(model, data):
    for number in data:
        account = model.query.filter_by(id=number).first()
        account.active = False
        db.session.commit()
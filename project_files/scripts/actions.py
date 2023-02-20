from project_files import db
from project_files import mail
from project_files import BLOCKED, USER, PRODUCT, EVENTS, DATA

from ..database import User, Blocked, Product

from flask_mail import Message

from datetime import datetime, date, timedelta

from ..scripts.functions import open_json, save_json 




def delete_rows(model, data):

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


def message(kind, sender, recipents, key):

    if kind == 'register':
        subject = 'Register message'
        body = f'Welcome {recipents}. This is your activation key {key}'

    if kind == 'no-reply':
        subject = 'no-reply-message'
        body = 'Do not reply for this message. This is only test.'

    if kind == 'code':
        subject = 'Forgotten password'
        body = f'This is your key {key}'

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
        path = USER
    elif model == Product:
        path = PRODUCT
    else:
        path = BLOCKED

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

    if model == User:

        data_from_file = open_json(file_path=USER)

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
            )

            whether_exist = model.query.filter_by(username=data['username']).first()
            
            if whether_exist == None:

                db.session.add(user)
                db.session.commit()

    elif model == Product:

        data_from_file = open_json(file_path=PRODUCT)

        for data in data_from_file:

            product = model(
                name=data['name'],
                category=data['category'],
                company=data['company'],
                price=data['price'],
            )
            
            whether_exist = model.query.filter_by(name=data['name']).first()
            
            if whether_exist == None:

                db.session.add(product)
                db.session.commit()

    elif model == Blocked:

        data_from_file = open_json(file_path=BLOCKED)

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


def delete_inactive_accounts():

    users = User.query.all()

    for user in users:

        if user.active ==  False:

            db.session.delete(user)
            db.session.commit()
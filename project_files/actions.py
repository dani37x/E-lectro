from project_files import db
from project_files import mail

from .database import User, Blocked

from flask_mail import Message

from datetime import datetime, date, timedelta


def delete_rows(model, data):
    print( model, data)
    for number in data:
        print(model.query.filter_by(id=number))
        model.query.filter_by(id=number).delete()
        db.session.commit()


def block_user(data):
    for user in data:
        user_to_block = User.query.get(id=user)
        # user_to_block.active = False
        
        new_row = Blocked(
            username=user_to_block.username,
            ip=user_to_block.ip,
            date=(datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
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
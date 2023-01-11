from project_files import db

from flask import request, abort, session
from flask_login import  current_user

from functools import wraps

from .database import Blocked



# def checker(username):
#     check = Blocked.query.filter_by(ip=request.remote_addr).first()
#     if check != None:
#         abort(403, description='You are banned')
#     check = Blocked.query.filter_by(username=username).first()
#     if check != None:
#         abort(403, description='You are banned')


def check_admin(name):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.username != 'Admin':
                abort(403)
            return f(*args, **kwargs)
        return wrapped
    return decorator


def check_user(name):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            check = Blocked.query.filter_by(ip=request.remote_addr).first()
            if check != None:
                abort(403)
            check = Blocked.query.filter_by(username=current_user.username).first()
            if check != None:
                abort(403)
            return f(*args, **kwargs)
        return wrapped
    return decorator


def not_null(field):
    if field != '' and field != None:
        return field
    else:
        raise ValueError      
 


def max_reminders():
    print(session['remind_one'], session['remind_two'])
    if session['remind_one'] == 'not set':
        session['remind_one']  = request.remote_addr
        return True
    if session['remind_two'] == 'not set':
        session['remind_two'] = request.remote_addr
        return True
    else:
        blocked = Blocked(username='anonymous', ip=request.remote_addr)
        # add to blocked timed ban
        db.session.add(blocked)
        db.session.commit()
        return False

    


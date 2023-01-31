from project_files import db

from flask import request, abort, session
from flask_login import  current_user

from functools import wraps

from .database import Blocked, User, Product

import json
import os

from datetime import datetime, date, timedelta


def check_admin(name):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.username != 'Admin' or current_user.username != 'admin':
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

            check = User.query.filter_by(username=current_user.username).first()
            if check.active == False:
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
    # print(session['remind_one'], session['remind_two'])
    if session['remind_one'] == 'not set':
        session['remind_one']  = request.remote_addr
        return True

    if session['remind_two'] == 'not set':
        session['remind_two'] = request.remote_addr
        return True

    else:
        blocked = Blocked(
            username='anonymous',
             ip=request.remote_addr,
              date=str((datetime.now() + timedelta(days=1)).strftime("%d-%m-%Y")))
        db.session.add(blocked)
        db.session.commit()
        session['remind_one'] == 'not set'
        session['remind_two'] == 'not set'
        return False



def save_to_json(username, ip, searched):
    path = 'D:\projekty\E-lectro\instance\data.json'

    objects_list = []

    with open(path) as fp:
        objects_list = json.load(fp)
        # for obj in objects_list:
        #     print(obj)

    objects_list.append({
            "username": f"{username}",
            "ip": f"{ip}",
            "searched": f"{searched}"
        })

    with open(path, 'w') as json_file:
        json.dump(objects_list, json_file, indent=4, separators=(',', ': '))
    

def string_to_date(date):
  return datetime.strptime(date, '%d-%m-%Y').date()


# todo
# add data if user was unbaned or error to json
def unblock(blocked_user):

    if date.today() > string_to_date(blocked_user.date):
        try:
            db.session.delete(blocked_user)
            db.session.commit()
            return True
        except Exception as e:
            print(e)
            return False
    else:
        return False


def save_error(error, site):

    path = 'D:\projekty\E-lectro\instance\events.json'

    objects_list = []

    with open(path) as fp:
        objects_list = json.load(fp)

    objects_list.append({
            "error": f"{error}",
            "time": f"{datetime.now()}",
            "site": f"{site}"
        })

    with open(path, 'w') as json_file:
        json.dump(objects_list, json_file, indent=4, separators=(',', ': '))